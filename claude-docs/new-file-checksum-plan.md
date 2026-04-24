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
- `bes__checksum__{algorithm}__1.0` → hex checksum bytes
- `__bes_mtime_bes__checksum__{algorithm}__1.0__` → mtime datetime bytes

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
  └── bf_metadata['bes__checksum__sha256__1.0']               ← L1: in-process dict (mtime-gated)
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
