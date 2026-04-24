# New File Metadata SQLite Plan

## 1. Requirements

### 1.1 Core Problem

Extended attributes (xattrs / ADS) are unreliable across platforms and filesystems. Specifically:

- Stripped silently when copying across filesystem boundaries (SMB, FAT, some NFS)
- Not supported on all filesystems (exFAT, FAT32, some network mounts)
- Behavior differs between macOS, Linux, and Windows in edge cases
- Read-only files cannot have xattrs written to them
- Some backup and sync tools discard them

The new system stores all metadata in an SQLite database keyed on the **sha256 checksum of the file content**, making it filesystem- and path-independent.

### 1.2 Goals

1. Replace xattr-backed metadata storage with SQLite-backed storage.
2. Expose the same logical API: get, set, keys, clear for arbitrary string key/value pairs.
3. Two layers:
   - **checksum layer** — accepts a sha256 hex string as the file identity key.
   - **file layer** — accepts a filename, computes its sha256 via the checksum infrastructure, and delegates to the checksum layer.
4. Plugs into the existing `bf_metadata_factory_base` / `bf_metadata_factory_registry` framework so factories continue to work unchanged.
5. CLI commands: `files metadata list|clear|set|get|keys`.
6. Vacuum support to prune old entries.
7. Single database for Phase 1; multi-database per filesystem in Phase 2 (proposal included).

### 1.3 Non-Goals

- Do not remove or modify the existing xattr-based metadata infrastructure yet. Leave `bf_attr`, `bf_metadata`, `bf_metadata_factory_base`, and related classes in place. Migration and cleanup is a separate task.
- Do not change existing `bf_metadata_key` naming convention (`domain__group__name__version`).

---

## 2. Existing Code Reference

### 2.1 Old API (fs layer — not to be reused directly)

`lib/bes/fs/_detail/file_metadata_db.py` — `file_metadata_db`

- Uses a per-file hash of the *filename string* (not content) as a table name suffix.
- One table per file, per `what` namespace: `{what}_{hash(filename)}`.
- Also keeps a `hash_to_filename` table mapping that hash back to the original path for debugging.
- Weaknesses: keyed on path (not content), creates unbounded number of tables, no vacuum.

`lib/bes/fs/file_metadata.py` — `file_metadata`

- Thin wrapper around `file_metadata_db` that normalises filenames.
- Not reused in the new design, kept for backward compatibility.

### 2.2 New Checksum Infrastructure

`lib/bes/files/checksum/bf_checksum_cache.py` — `bf_checksum_cache`
- `get_checksum(filename, algorithm)` — returns cached checksum string.
- Uses xattr backend if available on that filesystem, SQLite fingerprint otherwise.

`lib/bes/files/checksum/bf_checksum_algorithm.py` — `bf_checksum_algorithm`
- Constants: `MD5`, `SHA1`, `SHA256`; tuple `ALL`.

### 2.3 Existing Metadata Framework

`lib/bes/files/metadata/bf_metadata_factory_base.py`
- Abstract base class for factories. Subclass and implement `descriptions()`.

`lib/bes/files/metadata/bf_metadata_factory_registry.py`
- Global registry. Factories register themselves via the metaclass.

`lib/bes/files/metadata/bf_metadata_key.py`
- `domain__group__name__version` structured key, e.g. `bes__checksum__sha256__0.0`.

`lib/bes/files/metadata/bf_metadata.py`
- Current entry point for get/set; currently delegates to `bf_attr`. Not modified in Phase 1.

---

## 3. New Module Layout

All new files live under `lib/bes/files/metadata/`:

```
lib/bes/files/metadata/
  bf_metadata_database.py          # SQLite database, keyed on sha256 checksum
  bf_metadata_database_locator.py  # Decides which database file to use (Phase 1: single, Phase 2: per-filesystem)
  bf_metadata_store.py             # Checksum-key layer: get/set/keys/clear by sha256 string
  bf_metadata_file_store.py        # File layer: resolves sha256 from filename, delegates to bf_metadata_store
  bf_metadata_command_options.py   # CLI options
  bf_metadata_command_handler.py   # CLI command handler
  bf_metadata_command_factory.py   # CLI command factory
  bf_metadata_error.py             # (already exists — reuse)
```

---

## 4. Database Schema

### 4.1 Single Table Design

One table holds all metadata for all files. The file identity is the sha256 checksum of its content.

```sql
CREATE TABLE metadata_v1 (
  checksum   TEXT    NOT NULL,   -- sha256 hex of file content
  key        TEXT    NOT NULL,   -- arbitrary string key (e.g. bes__mime__media_type__1.0)
  value      TEXT    NOT NULL,   -- arbitrary string value
  stored_at  INTEGER NOT NULL,   -- unix timestamp (seconds), for vacuum
  PRIMARY KEY (checksum, key)
);

CREATE INDEX idx_checksum ON metadata_v1(checksum);
CREATE INDEX idx_stored_at ON metadata_v1(stored_at);
```

No separate metadata table for checksums is needed — schema versioning is handled by the `sqlite` wrapper's built-in `get_table_version` / `set_table_version` (the `__bes_table_version__` table), exactly as done in `bf_checksum_database`.

### 4.2 Schema Versioning

```
SCHEMA_VERSION = 1
```

On open:
1. If `metadata_v1` does not exist → create it, set version 1.
2. If it exists and version matches → proceed.
3. If version mismatches → drop `metadata_v1`, recreate at new version (all cached values are lost and recomputed on next access).

WAL mode is set immediately after connection: `PRAGMA journal_mode=WAL`.

---

## 5. Class Design

### 5.1 `bf_metadata_database`

Mirrors `bf_checksum_database` closely.

```python
class bf_metadata_database:
  SCHEMA_VERSION = 1
  _VACUUM_ROW_THRESHOLD = 50_000
  _VACUUM_AGE_DAYS = 180

  def __init__(self, database_path):
    # opens sqlite wrapper, sets WAL, calls _setup_schema(), _vacuum_if_needed()

  def get(self, checksum, key):
    # returns value string or None

  def set(self, checksum, key, value):
    # upsert; sets stored_at = now

  def delete(self, checksum, key=None):
    # if key is None: delete all rows for checksum
    # if key given: delete that specific (checksum, key) row

  def keys(self, checksum):
    # returns list of key strings for this checksum

  def get_all(self, checksum):
    # returns dict {key: value} for this checksum

  def row_count(self):
    # total rows in metadata_v1

  def close(self):
    # closes connection

  def _setup_schema(self): ...
  def _create_data_tables(self): ...
  def _vacuum_if_needed(self): ...
```

Threading: `threading.Lock()` per instance; `sqlite` wrapper instantiated with `check_same_thread=False`.

### 5.2 `bf_metadata_database_locator`

Decides which database file to open. Phase 1 is trivial; Phase 2 adds per-filesystem selection.

```python
class bf_metadata_database_locator:

  # Phase 1 — single global database
  DEFAULT_DATABASE_PATH = '~/.bes/metadata/metadata.db'

  @classmethod
  def database_path_for_file(clazz, filename):
    # Phase 1: always returns expanduser(DEFAULT_DATABASE_PATH)
    # Phase 2: returns per-filesystem path (see Section 6)
    return path.expanduser(clazz.DEFAULT_DATABASE_PATH)
```

### 5.3 `bf_metadata_store`

Checksum-key layer. Accepts a sha256 hex string as the file identity. Manages a pool of `bf_metadata_database` instances (one per database path).

```python
class bf_metadata_store:
  _shared_databases = {}
  _shared_databases_lock = threading.Lock()

  @classmethod
  def get(clazz, checksum, key):
    # returns value string or None

  @classmethod
  def set(clazz, checksum, key, value):
    # upserts into the single global database (Phase 1)

  @classmethod
  def delete(clazz, checksum, key=None):
    # deletes row or all rows for checksum

  @classmethod
  def keys(clazz, checksum):
    # returns list of key strings

  @classmethod
  def get_all(clazz, checksum):
    # returns dict

  @classmethod
  def _get_database(clazz, database_path):
    # returns shared bf_metadata_database instance, creating if needed
```

Phase 1: `_get_database` always resolves to `DEFAULT_DATABASE_PATH`.  
Phase 2: `database_path` will vary per filesystem; the pool handles one instance per path.

### 5.4 `bf_metadata_file_store`

File layer. Accepts a filename, resolves its sha256 via `bf_checksum_cache`, then delegates to `bf_metadata_store`.

```python
class bf_metadata_file_store:

  @classmethod
  def get(clazz, filename, key):
    checksum = bf_checksum_cache.get_checksum(filename, 'sha256')
    return bf_metadata_store.get(checksum, key)

  @classmethod
  def set(clazz, filename, key, value):
    checksum = bf_checksum_cache.get_checksum(filename, 'sha256')
    bf_metadata_store.set(checksum, key, value)

  @classmethod
  def delete(clazz, filename, key=None):
    checksum = bf_checksum_cache.get_checksum(filename, 'sha256')
    bf_metadata_store.delete(checksum, key)

  @classmethod
  def keys(clazz, filename):
    checksum = bf_checksum_cache.get_checksum(filename, 'sha256')
    return bf_metadata_store.keys(checksum)

  @classmethod
  def get_all(clazz, filename):
    checksum = bf_checksum_cache.get_checksum(filename, 'sha256')
    return bf_metadata_store.get_all(checksum)
```

---

## 6. Phase 2 Proposal — Per-Filesystem Databases

The motivation is the same as for `bf_checksum_database_locator`: keeping the database on the same filesystem as the files makes the cache portable (e.g. an external drive carries its own metadata cache). The logic mirrors `bf_checksum_database_locator` exactly:

1. Compute `st_dev` of the file's directory.
2. Walk up directory tree until `st_dev` changes — that is the volume root.
3. If the volume root is writable: store database at `{volume_root}/.bes_cache/metadata.db`.
4. If not writable: fall back to `~/.bes/metadata/{device_id_hex}.db` where `device_id_hex = f'{st_dev:016x}'`.
5. Cache `st_dev → database_path` in a class-level dict protected by a `threading.Lock`.

`bf_metadata_database_locator.database_path_for_file(filename)` is the single interface; `bf_metadata_store` calls it for every operation. Switching from Phase 1 to Phase 2 requires only changing the implementation of that one method.

---

## 7. Vacuum

### 7.1 Trigger

Vacuum runs at database open time, same as `bf_checksum_database`:

1. Count total rows.
2. If below `_VACUUM_ROW_THRESHOLD` (50,000): skip.
3. Compute cutoff: `now - _VACUUM_AGE_DAYS * 86400`.
4. Count rows older than cutoff.
5. If zero: skip.
6. Delete rows where `stored_at < cutoff`.
7. Commit. (SQLite WAL; no `VACUUM` statement needed.)

### 7.2 Parameters

| Constant | Value | Rationale |
|---|---|---|
| `_VACUUM_ROW_THRESHOLD` | 50,000 | Metadata entries are larger than checksum entries |
| `_VACUUM_AGE_DAYS` | 180 | Six months; files not seen in six months are unlikely to reappear |

### 7.3 Manual Vacuum

The CLI `files metadata clear <file>` deletes all metadata for a specific file (by its sha256). There is no CLI-level "purge all old entries" command in this plan, but `bf_metadata_database` exposes enough for one to be added later.

---

## 8. Integration with the Existing Factory Framework

The existing `bf_metadata_factory_base` / `bf_metadata_factory_registry` framework is unchanged. Factories that currently call `bf_checksum_cache.get_checksum` or `bf_attr` getters do not need to change.

The new store (`bf_metadata_file_store`) is an **alternative storage backend** that callers can use directly, independently of the factory registry. The factory registry is a description/lookup mechanism; storage is orthogonal to it.

Future work: once the xattr layer is fully replaced, `bf_metadata.get_metadata` would be updated to read from / write to `bf_metadata_file_store` instead of `bf_attr`. That is out of scope for this plan.

---

## 9. CLI Commands

Path: `files/metadata`

```
best2.py files/metadata list <file>
best2.py files/metadata clear <file>
best2.py files/metadata set <key> <value> <file>
best2.py files/metadata get <key> <file>
best2.py files/metadata keys <file>
```

### 9.1 Command Descriptions

| Command | Positional Args | Flags | Output |
|---|---|---|---|
| `list` | `file` | | Print all `key: value` pairs for the file |
| `clear` | `file` | `--yes` to skip confirmation | Delete all metadata for the file |
| `set` | `key value file` | | Upsert one key/value pair |
| `get` | `key file` | | Print value for key, or exit non-zero if not found |
| `keys` | `file` | | Print all keys, one per line |

`<file>` is always a single filename (not a directory glob). These commands operate on one file at a time. The sha256 is computed internally via `bf_metadata_file_store`.

### 9.2 `bf_metadata_command_options`

Follows `bf_file_resolver_cli_options` pattern using `bcli_options` + `bcli_options_desc`:

```
verbose  bool  default=False
  debug  bool  default=False
    yes  bool  default=False
```

### 9.3 `bf_metadata_command_factory`

Uses `bcli_command_factory_base`. Path: `files/metadata`.

`add_commands(subparsers)` registers: `list`, `clear`, `set`, `get`, `keys`.

`add_arguments(parser)` adds `--verbose`, `--debug`.

### 9.4 `bf_metadata_command_handler`

Methods:

```python
def _command_list(self, file, options): ...
def _command_clear(self, file, options): ...   # confirms unless --yes
def _command_set(self, key, value, file, options): ...
def _command_get(self, key, file, options): ...
def _command_keys(self, file, options): ...
```

Each resolves the filename to an absolute path, then delegates to `bf_metadata_file_store`.

---

## 10. Registration in `bes_application`

Add `bf_metadata_command_factory` to `parser_factories()` in `lib/bes/cli/bes_application.py`, alongside the existing `bf_checksum_command_factory`.

---

## 11. Resolved Design Decisions

**Q: Why sha256 as the key and not a fingerprint like `bf_checksum_fingerprint`?**  
A: Metadata must survive file moves and renames. The fingerprint (`bf_checksum_fingerprint`) encodes basename and mtime, so it changes when a file is renamed or touched. The sha256 of the content is path-independent and stable unless the content changes, which is exactly when the metadata should be recomputed anyway.

**Q: Why not one table per key namespace (like the old `file_metadata_db`)?**  
A: Unbounded table creation is an SQLite anti-pattern. A single flat table with a composite primary key and an index on `checksum` is simpler, vacuumable, and scales to millions of rows without schema changes.

**Q: Should value be TEXT or BLOB?**  
A: TEXT. All current metadata values are strings (checksums, mime types, dates encoded as ISO strings). BLOB adds complexity with no current benefit.

**Q: Why store `stored_at` rather than the file's mtime?**  
A: The record is keyed on content checksum, not path or mtime. Once the content is known, the metadata is valid regardless of when the file was last modified. `stored_at` is only used to prune very old entries that are unlikely to be needed again.

**Q: Phase 1 vs Phase 2 — when to switch?**  
A: Phase 1 (single global database) is sufficient for the immediate goal of replacing xattrs. Phase 2 (per-filesystem databases) is desirable for portability (external drives carrying their own cache) and should be implemented before this is used in production on multi-volume setups.

---

## 12. Unit Tests

### 12.1 `bf_metadata_database`

- `test_set_and_get` — set a key, get it back.
- `test_get_missing` — get a key that was never set returns `None`.
- `test_set_overwrites` — set same key twice, second value wins.
- `test_delete_by_key` — set two keys, delete one, other still present.
- `test_delete_all` — set two keys, delete all by checksum, both gone.
- `test_keys` — set three keys, `keys()` returns all three.
- `test_get_all` — set three keys, `get_all()` returns correct dict.
- `test_row_count` — set N rows, `row_count()` returns N.
- `test_schema_version` — open fresh database, schema version matches `SCHEMA_VERSION`.
- `test_schema_migration` — manually write wrong version into `__bes_table_version__`, reopen; tables recreated cleanly.
- `test_vacuum_skips_small_db` — row count below threshold, vacuum does not delete anything.
- `test_vacuum_deletes_old_rows` — insert rows with artificially old `stored_at`, row count above threshold; after vacuum old rows are gone.
- `test_vacuum_skips_no_old_rows` — all rows recent, vacuum does nothing even above threshold.

### 12.2 `bf_metadata_store`

- `test_set_and_get` — set via checksum key, get back.
- `test_get_missing_checksum` — unknown checksum returns `None`.
- `test_delete_by_key` — delete one key, other keys survive.
- `test_delete_all_keys` — delete with no key clears all entries for that checksum.
- `test_keys` — returns all keys for a checksum.
- `test_get_all` — returns all key/value pairs for a checksum.

### 12.3 `bf_metadata_file_store`

- `test_set_and_get` — write a file, set a key, get it back.
- `test_survives_rename` — write file, set key, rename file to a new path, get key via new path; should return same value (same sha256).
- `test_content_change_loses_metadata` — write file, set key, overwrite file with different content, get key; returns `None` (new checksum, no entry yet).
- `test_delete_by_key` — set two keys, delete one by key.
- `test_delete_all` — set two keys, clear file, both gone.
- `test_keys` — returns expected key list.
- `test_get_all` — returns expected dict.

### 12.4 CLI (`bf_metadata_command_handler`)

- `test_command_list_empty` — list on a file with no metadata prints nothing.
- `test_command_set_then_list` — set a key, list shows it.
- `test_command_get` — set a key, get returns value.
- `test_command_get_missing` — get on unknown key exits non-zero.
- `test_command_keys` — set two keys, keys command prints both.
- `test_command_clear` — set keys, clear, list shows nothing.
