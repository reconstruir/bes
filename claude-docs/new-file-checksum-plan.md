# New File Checksum System — Design Plan

## 1. Requirements

### Functional
- R1: Compute and cache file checksums for md5, sha1, sha256; extensible to new algorithms.
- R2: Cache is invalidated automatically when the file changes.
- R3: Works on Linux, macOS, Windows.
- R4: Works on all filesystem types: ext4, APFS, HFS+, NTFS, FAT32, exFAT, NFS, SMB, tmpfs.
- R5: Uses extended attributes (xattr on Linux/macOS) to store cached checksums when the filesystem supports them AND the file is writable by the current user.
- R6: Uses Windows Alternate Data Streams (ADS) to store cached checksums when on NTFS AND the file is writable.
- R7: Falls back to a SQLite database when xattr/ADS is unavailable or the file is not writable.
- R8: The SQLite fallback must correctly identify files across volume remounts and removable storage (i.e., must NOT use absolute path as the primary key).

### Non-Functional
- R9: Cache lookup is fast — must not read the full file on a cache hit.
- R10: Computing the cache key (file fingerprint) reads at most a small fixed number of bytes from the file.
- R11: Concurrent access from multiple processes must not corrupt the SQLite database (WAL mode).
- R12: The system integrates cleanly with the existing `bf_metadata` / `bf_attr` layered architecture.

---

## 2. Existing Code Review

| Component | Location | Role |
|---|---|---|
| `bf_checksum` | `files/checksum/bf_checksum.py` | Computes checksums via hashlib |
| `bf_checksum_db` | `files/checksum/bf_checksum_db.py` | SQLite cache keyed on `mtime_size_path` — **path-dependent, no fallback** |
| `bf_attr_getter_mixin` | `files/attr/bf_attr_getter_mixin.py` | `_do_get_cached_bytes` stores value + mtime in xattr/ADS |
| `bf_attr_sql_db` | `files/attr/bf_attr_sql_db.py` | SQLite storage for the attr layer keyed on an opaque `hash_key` |
| `bf_metadata_factory_checksum` | `files/metadata_factories/bf_metadata_factory_checksum.py` | Registers md5/sha1/sha256 via metadata factory |

### Problems with `bf_checksum_db`
- The `_make_hash_key` is `sha256(mtime_size_absolutepath)` — absolute path changes when a volume is remounted at a different mount point.
- Only stores sha256; adding new algorithms requires schema changes.
- No read-only-file fallback — relies only on the SQLite database without integrating with the xattr layer.

---

## 3. File Fingerprint Design

The **file fingerprint** is a compact, path-independent descriptor used as the primary cache key in the SQLite fallback. It must:
- Uniquely identify a specific version of a file's content with very high probability.
- Be cheap to compute (no full-file read).
- Be stable across remounts (no absolute path component).

### Fingerprint Version

`bf_checksum_fingerprint` carries an integer class constant `VERSION` (currently `1`). This version is the first field in the serialised form, so any change to the fingerprint algorithm, field set, or probe size produces a different `fingerprint_key` automatically — no explicit migration is needed.

### Fingerprint Fields

| Field | Serialised as | Notes |
|---|---|---|
| `version` | uint64 hex | Always `bf_checksum_fingerprint.VERSION`; currently `1` → `"0000000000000001"` |
| `basename` | raw string | `os.path.basename(filename)` — kept as-is, not encoded |
| `size` | uint64 hex | `stat.st_size` — always non-negative |
| `mtime_ns` | uint64 hex | `stat.st_mtime_ns` masked to unsigned 64-bit (see below) |
| `head_hash` | hex string | md5 of first 4096 bytes (or full file if smaller) |
| `tail_hash` | hex string | md5 of last 4096 bytes; same as `head_hash` if file ≤ 4096 bytes |

### Delimiter

`\x00` (null byte) is used between every field. It is the one byte that cannot appear in a filename on any OS — the kernel rejects it as a path component on Linux, macOS, and Windows. Common characters like `_` and `-` appear frequently in basenames and would create ambiguity (e.g., `report_2024_final` is indistinguishable from basename `report` with size `2024` and mtime `final`). `\x00` has no such ambiguity.

### Integer encoding

All integer fields are formatted as **16 lowercase hex digits** of their unsigned 64-bit two's complement representation:

```python
f'{value & 0xFFFF_FFFF_FFFF_FFFF:016x}'
```

This means:
- Positive values and zero are unchanged (leading-zero padded to 16 digits).
- Negative values — theoretically possible for `mtime_ns` on files with a modification time before 1970-01-01 (the Unix epoch) — map cleanly to their bitwise representation with no sign character. For example, `mtime_ns = -1` → `"ffffffffffffffff"`.
- The output is always exactly 16 characters, containing only `0–9` and `a–f`, which cannot collide with `\x00` or with `basename`.
- No sign ambiguity exists anywhere in the serialised string.

`size` is always non-negative (`stat.st_size` ≥ 0 by definition), so the masking has no practical effect there. It is applied uniformly for simplicity.

### Serialised form (hash input only — never stored)

```
{version}\x00{basename}\x00{size}\x00{mtime_ns}\x00{head_hash}\x00{tail_hash}
```

where `version`, `size`, and `mtime_ns` are 16-digit hex strings, and `head_hash` / `tail_hash` are 32-character md5 hex strings. This string is sha256-hashed to produce the fixed-length `fingerprint_key` and then discarded. The `\x00`-delimited form never touches the database.

The `fingerprint_version` integer is also stored as its own column in the database (see Section 4.2) so that stale rows from an old fingerprint version can be identified and removed during vacuum without recomputing keys.

**Why md5 for head/tail?** It is fast and the purpose here is cache invalidation, not security. Collision probability for this use case is negligible.

**Why not include inode or device ID?** inode changes on copy-and-replace (many editors, rsync `--checksum`), and device ID changes on remount — both would cause spurious cache misses.

**Limitation:** Two different files with the same basename, size, mtime_ns, first and last 4096 bytes will collide. For a checksum cache this is acceptable — the worst outcome is returning a stale cached value, not data corruption.

---

## 4. Storage Backends

### 4.1 Xattr / ADS Backend (existing, unchanged)

Already implemented in `bf_attr_getter_mixin._do_get_cached_bytes`. Stores:
- `bes__checksum__{algorithm}__0.0` → hex checksum bytes
- `__bes_mtime_bes__checksum__{algorithm}__0.0__` → mtime datetime bytes

Requires: xattr/ADS support on filesystem + file is writable.

### 4.2 New: SQLite Fingerprint Backend

#### Schema versioning

The database carries its own schema version, stored in a `database_metadata` table that is always the first table created:

```sql
CREATE TABLE database_metadata (
  key    TEXT PRIMARY KEY NOT NULL,
  value  TEXT NOT NULL
);
-- Populated on creation:
-- INSERT INTO database_metadata VALUES ('schema_version', '1');
```

`bf_checksum_database` defines `SCHEMA_VERSION = 1` as a class constant. On every open:

1. Read `schema_version` from `database_metadata`.
2. If equal to `SCHEMA_VERSION`: proceed normally.
3. If less than `SCHEMA_VERSION` (upgrade needed) or greater (downgrade — someone ran a newer binary then reverted): drop all non-metadata tables, recreate them at `SCHEMA_VERSION`, update the stored version. Since this is a cache, discarding rows is always safe — they will be recomputed on next access.

This avoids complex migration logic while still detecting schema mismatches correctly.

#### Schema

```sql
CREATE TABLE database_metadata (
  key    TEXT PRIMARY KEY NOT NULL,
  value  TEXT NOT NULL
);

CREATE TABLE checksums_v1 (
  fingerprint_key      TEXT NOT NULL,
  fingerprint_version  INTEGER NOT NULL,
  algorithm            TEXT NOT NULL,
  checksum             TEXT NOT NULL,
  cached_at            INTEGER NOT NULL,
  PRIMARY KEY (fingerprint_key, algorithm)
);

CREATE INDEX idx_fingerprint_version ON checksums_v1(fingerprint_version);
```

The `algorithm` column allows any algorithm to be added without a schema change. The `fingerprint_version` column enables targeted vacuum: `DELETE FROM checksums_v1 WHERE fingerprint_version < {current_version}` removes all orphaned rows from old fingerprint formats without recomputing any keys. The index on `fingerprint_key` is omitted — it is the leading part of the primary key and SQLite indexes it implicitly.

---

## 5. Backend Selection Logic

```
for a given (filename, algorithm):

1. Is the file writable by the current user?
   AND does the filesystem support xattr/ADS?
   → use xattr/ADS backend (existing _do_get_cached_bytes path)

2. Otherwise:
   → use SQLite fingerprint backend
      → pick database file (see Section 6)
      → compute fingerprint_key (cheap)
      → look up (fingerprint_key, algorithm) in database
         → HIT: return cached value
         → MISS: compute full checksum, INSERT into database, return value
```

The writability check uses `os.access(filename, os.W_OK)`. The xattr availability check attempts a probe xattr set/get/remove on a temp file on the same filesystem (cached per `st_dev`).

---

## 6. SQLite Database Placement Strategy

This is the hardest problem. Requirements:
- The database must be findable given only a file path.
- The database must survive volume remounts at different mount points.
- Works for removable volumes (USB drives, SD cards, network mounts).
- Works when the user has no write access to the volume root.

### Strategy: Tiered placement

**Tier 1 — On-volume database** (preferred for removable/external volumes):

Try to create `.bes_cache/checksums.sqlite` in the root of the volume that contains the file. To find the volume root:
- Linux/macOS: walk up from `dirname(filename)` until `os.stat(parent).st_dev != os.stat(current).st_dev`, then use `current` as the volume root.
- Windows: `os.path.splitdrive(filename)[0] + '\\'`

If the volume root is writable: place database at `{volume_root}/.bes_cache/checksums.sqlite`.

**Tier 2 — Global user database** (fallback for read-only volumes, network mounts):

`~/.bes/checksums/{volume_id}.sqlite`

where `volume_id` is a stable identifier for the volume:
- Linux: sha256 of the filesystem UUID from `/proc/mounts` + `blkid` (or fall back to `st_dev` cast to string)
- macOS: volume UUID from `diskutil info -plist / | grep VolumeUUID` (or `st_dev`)
- Windows: volume serial number from `GetVolumeInformation`

If the volume cannot be identified stably (e.g., network mounts with no UUID), fall back to:
`~/.bes/checksums/net_{sha256(first_256_chars_of_mountpoint)}.sqlite`

### Database Locator Class: `bf_checksum_database_locator`

```python
class bf_checksum_database_locator:
  @classmethod
  def database_path_for_file(clazz, filename) -> str:
    'Return the path to the SQLite database that should store checksums for filename.'
```

Caches results per `st_dev` to avoid repeated filesystem walks.

---

## 7. Hash Algorithm Registry

New class `bf_checksum_algorithm` (enum-like, extensible):

```python
class bf_checksum_algorithm:
  MD5    = 'md5'
  SHA1   = 'sha1'
  SHA256 = 'sha256'
  # new entries added here; no database migration needed
```

The `bf_checksum.checksum(filename, algorithm)` method already uses `hashlib.new(algorithm)` so it is already open to any hashlib-supported algorithm.

---

## 8. API Design

### 8.1 Low-level: `bf_checksum_cache`

New class in `lib/bes/files/checksum/bf_checksum_cache.py`:

```python
class bf_checksum_cache:
  @classmethod
  def get_checksum(clazz, filename, algorithm) -> str:
    'Return cached checksum for filename and algorithm, computing it if needed.'

  @classmethod
  def invalidate(clazz, filename, algorithm=None):
    'Remove cached checksum(s) for filename. If algorithm is None, remove all.'

  @classmethod
  def has_cached(clazz, filename, algorithm) -> bool:
    'Return True if a fresh cached checksum exists without computing it.'
```

Internally selects xattr or SQLite backend per the logic in Section 5.

### 8.2 `bf_entry` properties (unchanged API, new implementation)

```python
@property
def checksum_md5(self) -> str: ...

@property
def checksum_sha1(self) -> str: ...

@property
def checksum_sha256(self) -> str: ...
```

These continue to work via `bf_metadata` → `bf_metadata_factory_checksum`, which internally calls `bf_checksum_cache.get_checksum`.

### 8.3 `bf_metadata_factory_checksum` (updated)

Replace the direct `bf_checksum.checksum(f, algorithm)` calls with `bf_checksum_cache.get_checksum(f, algorithm)`. The metadata layer's own mtime-caching on top of xattr continues to work as a fast in-process L1 cache; `bf_checksum_cache` becomes the L2 persistent cache.

---

## 9. Caching Layers Summary

```
bf_entry.checksum_sha256
  └── bf_metadata['bes__checksum__sha256__0.0']               ← L1: in-process dict (mtime-gated)
        └── bf_metadata_factory_checksum.getter(f)
              └── bf_checksum_cache.get_checksum(f, 'sha256')
                    ├── xattr/ADS backend                     ← L2a: on-file (writable files)
                    └── SQLite fingerprint backend             ← L2b: database (read-only or no xattr)
                          └── bf_checksum.checksum(f, 'sha256')  ← L3: full read (cache miss)
```

---

## 10. New Files / Modules

```
lib/bes/files/checksum/
  bf_checksum.py                        (existing, unchanged)
  bf_checksum_algorithm.py              (NEW: algorithm name constants)
  bf_checksum_cache.py                  (NEW: unified get/invalidate API)
  bf_checksum_database.py               (REPLACE: new schema, multi-algorithm, fingerprint key)
  bf_checksum_database_locator.py       (NEW: finds database path for a given file)
  bf_checksum_fingerprint.py            (NEW: computes the file fingerprint key)
  bf_global_checksum_db.py              (REMOVE: replaced by bf_checksum_database_locator)
```

Existing files that change:
- `lib/bes/files/metadata_factories/bf_metadata_factory_checksum.py` — call `bf_checksum_cache` instead of `bf_checksum` directly.
- `lib/bes/files/checksum/__init__.py` — export new classes.

---

## 11. Migration from Old `bf_checksum_db`

`bf_global_checksum_db` / `bf_checksum_db` are used in a small number of places. Replace call sites with `bf_checksum_cache.get_checksum(filename, 'sha256')`. Old databases at `~/.bes/bes_global_checksum_db.sqlite` can be ignored (they will simply not be read; entries expire on next access).

The old attribute keys (`bes_checksum_md5`, `bes_checksum_sha1`) are already handled by `bf_metadata_factory_checksum`'s `old_getter` lambda — no change needed there.

---

## 12. Versioning Summary

Two independent version numbers, each evolving separately:

| Version | Constant | Location | What it guards |
|---|---|---|---|
| `fingerprint_version` | `bf_checksum_fingerprint.VERSION = 1` | class constant | The fingerprint serialisation format (fields, probe size, hash algorithm for head/tail) |
| `schema_version` | `bf_checksum_database.SCHEMA_VERSION = 1` | class constant | The SQLite table layout |

**How they interact on a version bump:**

- *Fingerprint version bumps* (e.g., probe size changes from 4096 to 8192): all old `fingerprint_key` values are different from the new ones, so lookups naturally miss and recompute. Old rows are orphaned but harmless; the `fingerprint_version` index makes the next vacuum cheap (`DELETE … WHERE fingerprint_version < N`).

- *Schema version bumps* (e.g., a new column is added): the `database_metadata` check on open detects the mismatch, drops and recreates all data tables at the new version, and resets `schema_version`. All cached values are lost and will be recomputed on next access.

- *Both bump together*: the schema upgrade runs first (on open), producing an empty database at the new schema, into which new fingerprint-versioned rows are then written.

Neither version is ever stored in a filename. Version detection is always done by reading the database itself.

---

## 13. Implementation Order

1. `bf_checksum_algorithm` — trivial, unblocks everything else.
2. `bf_checksum_fingerprint` — pure function, easy to unit-test.
3. `bf_checksum_database` — new schema; test with in-memory SQLite.
4. `bf_checksum_database_locator` — test with temp dirs on different mock `st_dev` values.
5. `bf_checksum_cache` — wire fingerprint + locator + xattr selection logic.
6. Update `bf_metadata_factory_checksum`.
7. Remove `bf_global_checksum_db`, update call sites.
8. Integration tests: read-only file, writable file, file on tmpfs (no xattr), file on FAT (no xattr).

---

## 14. Resolved Design Decisions

- **Fingerprint probe size**: `bf_checksum_fingerprint.HEAD_TAIL_PROBE_BYTES = 4096` as a class-level constant. Not configurable until there is a demonstrated need; fingerprint version bump handles cache invalidation automatically if the value ever changes.

- **Stale database entries**: Vacuum triggers lazily on open when BOTH conditions are true: total row count exceeds 10,000 AND at least one row has `cached_at` older than 90 days. When triggered, delete all rows with `cached_at` older than 90 days. Both conditions required to avoid vacuuming small active databases on every open.

- **Thread safety**: Open each database connection with `check_same_thread=False` and protect it with a per-instance `threading.Lock`. One shared connection per database file path. WAL mode handles concurrent readers from separate processes.

- **FAT mtime granularity**: Handled by `head_hash`. No special-casing needed.

- **Network filesystem head/tail read**: No flag. The head/tail read is at most 8 KB and only occurs on a fingerprint cache miss, which itself only occurs when `mtime_ns` changes. The common path over slow NFS reads nothing.

- **xattr availability probe**: Create a small temp file in the same directory as the target file, attempt xattr set/get/remove, delete the temp file immediately. If the temp file cannot be created (directory not writable or filesystem read-only), treat the probe result as "xattr unavailable — use SQLite." Cache result per `st_dev`.

- **Network mount volume identifier**: For network mounts with no stable UUID, extract server hostname from `/proc/mounts` or `mount` output and use `sha256(hostname)` as the volume identifier. If hostname extraction fails, fall back to `~/.bes/checksums/unknown.sqlite` — one shared database for all unidentifiable volumes, relying on the fingerprint's path-independence for correctness.

- **`invalidate()` for the SQLite backend**: Compute the fingerprint key from the current file state and delete all rows with that key (`DELETE FROM checksums_v1 WHERE fingerprint_key = ?`), which removes all cached algorithms at once. If `algorithm` is specified, add `AND algorithm = ?`. If the file no longer exists, do nothing — the row is orphaned and will be removed by the next vacuum.

- **`bf_checksum_database_locator` cache after remount**: Not a problem. After a remount, the new `st_dev` value gets a fresh cache entry pointing to the correct database. The old entry for the previous `st_dev` is simply never accessed again.

---

## 15. Unit Tests

All test files live under `tests/lib/bes/files/checksum/`. Each class gets its own test file named `test_{class_name}.py`.

---

### 15.1 `test_bf_checksum_algorithm`

```
test_constants_exist
  assert bf_checksum_algorithm.MD5   == 'md5'
  assert bf_checksum_algorithm.SHA1  == 'sha1'
  assert bf_checksum_algorithm.SHA256 == 'sha256'

test_all_list_contains_all_three
  assert set(bf_checksum_algorithm.ALL) == {'md5', 'sha1', 'sha256'}
```

---

### 15.2 `test_bf_checksum_fingerprint`

```
test_key_is_deterministic
  write temp file with fixed content
  key1 = bf_checksum_fingerprint.make_key(tmp)
  key2 = bf_checksum_fingerprint.make_key(tmp)
  assert key1 == key2

test_key_is_path_independent
  write temp file with fixed content
  compute key at original path
  copy file to a second temp path (same content, same mtime — use os.utime to clone mtime)
  assert keys are equal

test_content_change_invalidates_key
  write temp file with content A
  key_a = bf_checksum_fingerprint.make_key(tmp)
  overwrite same file with content B (different size)
  key_b = bf_checksum_fingerprint.make_key(tmp)
  assert key_a != key_b

test_mtime_change_invalidates_key
  write temp file
  key_before = bf_checksum_fingerprint.make_key(tmp)
  advance mtime by 1 second with os.utime
  key_after = bf_checksum_fingerprint.make_key(tmp)
  assert key_before != key_after

test_basename_change_invalidates_key
  write temp file named 'alpha.txt'
  copy to 'beta.txt' in same dir (clone mtime)
  assert keys differ despite identical content and mtime

test_version_change_invalidates_key
  compute key normally (VERSION == 1)
  monkeypatch bf_checksum_fingerprint.VERSION = 2
  assert key differs from VERSION-1 key
  restore VERSION

test_empty_file
  write empty temp file
  key = bf_checksum_fingerprint.make_key(tmp)
  assert isinstance(key, str) and len(key) == 64  # sha256 hex

test_small_file_under_probe_size
  write temp file with 100 bytes
  key = bf_checksum_fingerprint.make_key(tmp)
  assert head_hash == tail_hash (confirmed by inspecting _compute_head_tail directly)

test_large_file_over_probe_size
  write temp file with 10 KB of data
  key = bf_checksum_fingerprint.make_key(tmp)
  assert key is a 64-char hex string
  assert head_hash != tail_hash (they cover different regions)

test_pre_epoch_mtime
  write temp file
  set mtime to -1 nanosecond before epoch via os.utime(tmp, ns=(-1, -1))
  key = bf_checksum_fingerprint.make_key(tmp)
  assert isinstance(key, str) and len(key) == 64

test_head_tail_probe_bytes_constant
  assert bf_checksum_fingerprint.HEAD_TAIL_PROBE_BYTES == 4096
```

---

### 15.3 `test_bf_checksum_database`

All tests use an in-memory SQLite path (`:memory:`) or a temp-file path — never a real on-disk location.

```
test_create_empty_database
  db = bf_checksum_database(':memory:')
  assert db.row_count() == 0

test_schema_version_in_metadata
  db = bf_checksum_database(':memory:')
  assert db.schema_version() == bf_checksum_database.SCHEMA_VERSION

test_set_and_get_checksum
  db = bf_checksum_database(':memory:')
  db.set_checksum('key1', 1, 'md5', 'deadbeef' * 4)
  result = db.get_checksum('key1', 'md5')
  assert result == 'deadbeef' * 4

test_get_missing_key_returns_none
  db = bf_checksum_database(':memory:')
  assert db.get_checksum('no_such_key', 'md5') is None

test_set_overwrites_existing
  db = bf_checksum_database(':memory:')
  db.set_checksum('key1', 1, 'md5', 'aaaa')
  db.set_checksum('key1', 1, 'md5', 'bbbb')
  assert db.get_checksum('key1', 'md5') == 'bbbb'

test_multiple_algorithms_same_key
  db = bf_checksum_database(':memory:')
  db.set_checksum('key1', 1, 'md5',    'aaa')
  db.set_checksum('key1', 1, 'sha256', 'bbb')
  assert db.get_checksum('key1', 'md5')    == 'aaa'
  assert db.get_checksum('key1', 'sha256') == 'bbb'

test_delete_by_key_removes_all_algorithms
  db = bf_checksum_database(':memory:')
  db.set_checksum('key1', 1, 'md5',    'aaa')
  db.set_checksum('key1', 1, 'sha256', 'bbb')
  db.delete_checksum('key1')
  assert db.get_checksum('key1', 'md5')    is None
  assert db.get_checksum('key1', 'sha256') is None

test_delete_by_key_and_algorithm
  db = bf_checksum_database(':memory:')
  db.set_checksum('key1', 1, 'md5',    'aaa')
  db.set_checksum('key1', 1, 'sha256', 'bbb')
  db.delete_checksum('key1', algorithm='md5')
  assert db.get_checksum('key1', 'md5')    is None
  assert db.get_checksum('key1', 'sha256') == 'bbb'

test_schema_version_mismatch_recreates_database
  db_path = make_temp_file(suffix='.sqlite')
  db_v1 = bf_checksum_database(db_path)
  db_v1.set_checksum('key1', 1, 'md5', 'aaa')
  db_v1.close()
  # Write a schema_version > SCHEMA_VERSION into database_metadata to simulate a future schema
  # (inject directly with sqlite3)
  connection = sqlite3.connect(db_path)
  connection.execute("UPDATE database_metadata SET value = '999' WHERE key = 'schema_version'")
  connection.commit()
  connection.close()
  # Re-open: should detect mismatch, drop tables, recreate at current version
  db_v2 = bf_checksum_database(db_path)
  assert db_v2.schema_version() == bf_checksum_database.SCHEMA_VERSION
  assert db_v2.get_checksum('key1', 'md5') is None  # old data gone

test_vacuum_not_triggered_below_row_threshold
  db = bf_checksum_database(':memory:')
  # Insert 5000 rows all older than 91 days
  past_time = int(time.time()) - 91 * 86400
  for i in range(5000):
    db._connection.execute(
      "INSERT OR REPLACE INTO checksums_v1 VALUES (?, ?, ?, ?, ?)",
      (f'key{i}', 1, 'md5', 'aaa', past_time)
    )
  db._connection.commit()
  db._vacuum_if_needed()
  assert db.row_count() == 5000  # vacuum not triggered (< 10000 rows)

test_vacuum_triggered_when_both_conditions_met
  db = bf_checksum_database(':memory:')
  past_time = int(time.time()) - 91 * 86400
  recent_time = int(time.time())
  # Insert 10001 rows: 5000 old + 5001 recent
  for i in range(5000):
    db._connection.execute(
      "INSERT OR REPLACE INTO checksums_v1 VALUES (?, ?, ?, ?, ?)",
      (f'old_key{i}', 1, 'md5', 'aaa', past_time)
    )
  for i in range(5001):
    db._connection.execute(
      "INSERT OR REPLACE INTO checksums_v1 VALUES (?, ?, ?, ?, ?)",
      (f'new_key{i}', 1, 'md5', 'bbb', recent_time)
    )
  db._connection.commit()
  db._vacuum_if_needed()
  assert db.row_count() == 5001  # only old rows removed

test_wal_mode_enabled
  db_path = make_temp_file(suffix='.sqlite')
  db = bf_checksum_database(db_path)
  cursor = db._connection.execute("PRAGMA journal_mode")
  assert cursor.fetchone()[0] == 'wal'

test_thread_safety_concurrent_writes
  db = bf_checksum_database(':memory:')
  errors = []
  def write_row(index):
    try:
      db.set_checksum(f'key{index}', 1, 'md5', f'value{index}')
    except Exception as exception:
      errors.append(exception)
  threads = [threading.Thread(target=write_row, args=(i,)) for i in range(50)]
  [thread.start() for thread in threads]
  [thread.join() for thread in threads]
  assert errors == []
  assert db.row_count() == 50
```

---

### 15.4 `test_bf_checksum_database_locator`

```
test_returns_path_for_writable_directory
  tmp_dir = make_temp_dir()
  db_path = bf_checksum_database_locator.get_database_path(tmp_dir + '/dummy_file.txt')
  assert db_path is not None
  assert isinstance(db_path, str)

test_same_filesystem_returns_same_path
  tmp_dir = make_temp_dir()
  file_a = make_temp_file(dir=tmp_dir)
  file_b = make_temp_file(dir=tmp_dir)
  path_a = bf_checksum_database_locator.get_database_path(file_a)
  path_b = bf_checksum_database_locator.get_database_path(file_b)
  assert path_a == path_b  # same st_dev → same database

test_result_is_cached_per_st_dev
  # Call get_database_path twice for the same file; the second call must not re-probe xattr
  tmp_file = make_temp_file()
  bf_checksum_database_locator._clear_cache()
  path1 = bf_checksum_database_locator.get_database_path(tmp_file)
  path2 = bf_checksum_database_locator.get_database_path(tmp_file)
  assert path1 == path2

test_on_volume_tier_used_when_directory_writable
  # On a normal writable temp dir the result is the on-volume .bes_cache/checksums.sqlite path
  tmp_file = make_temp_file()
  db_path = bf_checksum_database_locator.get_database_path(tmp_file)
  assert '.bes_cache' in db_path
  assert db_path.endswith('checksums.sqlite')

test_home_tier_used_when_directory_not_writable
  # Make parent directory read-only, expect fallback to home-tier path
  tmp_dir = make_temp_dir()
  tmp_file = make_temp_file(dir=tmp_dir)
  os.chmod(tmp_dir, 0o555)
  try:
    db_path = bf_checksum_database_locator.get_database_path(tmp_file)
    assert '.bes' in db_path
    assert '.bes_cache' not in db_path
  finally:
    os.chmod(tmp_dir, 0o755)
```

---

### 15.5 `test_bf_checksum_cache`

These are integration tests — they write real files, use real xattr (where available), and hit real SQLite.

```
test_get_checksum_md5
  tmp_file = make_temp_file(content=b'hello world')
  result = bf_checksum_cache.get_checksum(tmp_file, 'md5')
  assert result == '5eb63bbbe01eeed093cb22bb8f5acdc3'

test_get_checksum_sha256
  tmp_file = make_temp_file(content=b'hello world')
  result = bf_checksum_cache.get_checksum(tmp_file, 'sha256')
  assert result == 'b94d27b9934d3e08a52e52d7da7dabfac484efe04294e576fb246a79069d4ef7' (known sha256)

test_second_call_returns_cached_value_without_file_read
  tmp_file = make_temp_file(content=b'hello world')
  result1 = bf_checksum_cache.get_checksum(tmp_file, 'md5')
  # Replace file content without changing mtime to simulate a stale-read scenario
  # (verifies cache hit does not re-read file)
  with open(tmp_file, 'wb') as file_handle:
    file_handle.write(b'different')
  os.utime(tmp_file, ns=(original_mtime_ns, original_mtime_ns))
  result2 = bf_checksum_cache.get_checksum(tmp_file, 'md5')
  assert result1 == result2  # served from cache, not re-read

test_file_change_invalidates_xattr_cache
  tmp_file = make_temp_file(content=b'version1')
  result1 = bf_checksum_cache.get_checksum(tmp_file, 'md5')
  # Overwrite with different content and advance mtime
  time.sleep(0.01)
  with open(tmp_file, 'wb') as file_handle:
    file_handle.write(b'version2')
  result2 = bf_checksum_cache.get_checksum(tmp_file, 'md5')
  assert result1 != result2

test_has_cached_false_before_first_call
  tmp_file = make_temp_file(content=b'data')
  bf_checksum_cache.invalidate(tmp_file)
  assert bf_checksum_cache.has_cached(tmp_file, 'md5') is False

test_has_cached_true_after_get
  tmp_file = make_temp_file(content=b'data')
  bf_checksum_cache.get_checksum(tmp_file, 'md5')
  assert bf_checksum_cache.has_cached(tmp_file, 'md5') is True

test_invalidate_single_algorithm
  tmp_file = make_temp_file(content=b'data')
  bf_checksum_cache.get_checksum(tmp_file, 'md5')
  bf_checksum_cache.get_checksum(tmp_file, 'sha256')
  bf_checksum_cache.invalidate(tmp_file, algorithm='md5')
  assert bf_checksum_cache.has_cached(tmp_file, 'md5')    is False
  assert bf_checksum_cache.has_cached(tmp_file, 'sha256') is True

test_invalidate_all_algorithms
  tmp_file = make_temp_file(content=b'data')
  bf_checksum_cache.get_checksum(tmp_file, 'md5')
  bf_checksum_cache.get_checksum(tmp_file, 'sha256')
  bf_checksum_cache.invalidate(tmp_file)
  assert bf_checksum_cache.has_cached(tmp_file, 'md5')    is False
  assert bf_checksum_cache.has_cached(tmp_file, 'sha256') is False

test_invalidate_nonexistent_file_does_nothing
  nonexistent = '/tmp/no_such_file_abc123.txt'
  bf_checksum_cache.invalidate(nonexistent)  # must not raise

test_sqlite_fallback_used_on_readonly_file
  # Mark file read-only so xattr set will fail → falls back to SQLite
  tmp_file = make_temp_file(content=b'readonly data')
  os.chmod(tmp_file, 0o444)
  try:
    result = bf_checksum_cache.get_checksum(tmp_file, 'md5')
    assert isinstance(result, str) and len(result) == 32
    assert bf_checksum_cache.has_cached(tmp_file, 'md5') is True
  finally:
    os.chmod(tmp_file, 0o644)
```

---

### 15.6 `test_bf_metadata_factory_checksum`

These verify that the factory delegates correctly to `bf_checksum_cache` instead of calling `bf_checksum` directly.

```
test_md5_via_metadata
  tmp_file = make_temp_file(content=b'hello world')
  entry = bf_entry(tmp_file)
  assert entry.checksum_md5 == '5eb63bbbe01eeed093cb22bb8f5acdc3'

test_sha1_via_metadata
  tmp_file = make_temp_file(content=b'hello world')
  entry = bf_entry(tmp_file)
  assert entry.checksum_sha1 == '2aae6c69ec0bdd100a6b9a0fcd7a1b7e3e5e6a58' (known sha1)

test_sha256_via_metadata
  tmp_file = make_temp_file(content=b'hello world')
  entry = bf_entry(tmp_file)
  assert entry.checksum_sha256 == known_sha256_value

test_has_checksum_true_after_access
  tmp_file = make_temp_file(content=b'hello world')
  entry = bf_entry(tmp_file)
  _ = entry.checksum_md5
  assert entry.has_checksum_md5 is True

test_factory_calls_cache_not_raw_checksum
  # Confirm bf_checksum_cache.get_checksum is invoked rather than bf_checksum.checksum
  tmp_file = make_temp_file(content=b'data')
  with unittest.mock.patch('bes.files.checksum.bf_checksum_cache.get_checksum') as mock_get:
    mock_get.return_value = 'mock_md5_value'
    entry = bf_entry(tmp_file)
    _ = entry.checksum_md5
    mock_get.assert_called_once_with(tmp_file, 'md5')
```

---

### 15.7 Changes to existing `_file_attributes_xattr.py` and related tests

The `com.apple.provenance` system key filter was already added (earlier in this session). Tests for it belong in the existing xattr test files. The key requirement to verify:

```
test_keys_does_not_include_com_apple_system_keys
  tmp_file = make_temp_file()
  xattr_instance.set(tmp_file, 'user_key', b'value')
  keys = xattr_instance.keys(tmp_file)
  for key in keys:
    assert not key.startswith('com.apple.')
  assert 'user_key' in keys
```

This applies to:
- `test_file_attributes_xattr.py` (the `_file_attributes_xattr` classmethod-style class)
- `test_bf_attr_getter_xattr.py` (the `_bf_attr_getter_xattr` instance-style class)
- `test_xattr_exe.py` (the `xattr_exe` CLI wrapper class)
