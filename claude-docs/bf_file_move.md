# bf_file_mover — Design Proposal

## Overview

A move framework that relocates files from a source directory to a destination directory with two-phase semantics: an immediate same-filesystem `os.rename` to a staging area (making the file "disappear" from its original location atomically), followed by an async cross-device copy to the true destination.  A SQLite database tracks every operation from submission through completion.

---

## Module layout

```
lib/bes/files/move/
  bf_file_mover.py               — public API; instantiated with a database path
  bf_file_mover_database.py      — SQLite persistence layer
  bf_file_mover_database_locator.py  — convenience helper: suggests a database path for a given context
  bf_file_mover_operation.py     — dataclass representing one move record
  bf_file_mover_options.py       — configuration dataclass (chunk_size, callbacks)
  bf_file_mover_status.py        — enum: pending / staging_done / copying / paused / done / failed / expired
  bf_file_mover_worker.py        — background thread worker

tests/lib/bes/files/move/
  test_bf_file_mover.py          — full integration and unit tests (see test coverage section)
  test_bf_file_mover_database.py — database layer tests in isolation

lib/bes/files/core/
  bf_volume_locator.py          — shared device-walk + path resolution (refactored from bf_checksum_database_locator)
```

`bf_file_mover_database_locator` is a thin convenience class — it suggests a path like `~/.bes/move/move.sqlite` or a per-project path, but the caller is free to ignore it and pass any path they like.  It does not affect the move logic.

---

## Staging location and database locator

### The problem

The checksum code in `bf_checksum_database_locator.py` and the move framework share the same need: given a file on an arbitrary filesystem/volume, find a writable location **on that same device** to place a working artefact (checksum db vs. staging area + move db).  The logic to walk up to the volume root and fall back to `~/.bes/<device_id>/` is generic.

### Proposed refactor

Extract a shared helper:

```
lib/bes/files/core/bf_volume_locator.py
```

`bf_volume_locator` exposes two classmethods:

```python
# Returns a writable directory on the same device as filename.
# Priority: <volume_root>/.bes_cache/<purpose>/ → ~/.bes/<device_hex>/<purpose>/
bf_volume_locator.directory_for_file(filename, purpose)   # → str path
bf_volume_locator.database_path_for_file(filename, purpose, db_name)  # → str path
```

`bf_checksum_database_locator` becomes a thin wrapper:

```python
bf_volume_locator.database_path_for_file(filename, 'checksums', 'checksums.sqlite')
```

The move framework uses only the directory form — the database is global, not per-device:

```python
bf_volume_locator.directory_for_file(filename, 'move_staging')
```

This eliminates duplicated device-walk logic and gives a consistent `.bes_cache/` tree on each volume.

---

## Constraints

- **Basename must be preserved.** `os.path.basename(destination_path)` must equal `os.path.basename(source_path)`. `move()` validates this and raises `ValueError` if they differ. Moves that rename a file are out of scope — they are two operations (move + rename) and conflating them complicates recovery.

---

## Staging area semantics

When a move is submitted for `/mnt/music/rips/foo.flac → /mnt/archive/foo.flac`:

1. Validate that `os.path.basename(destination_path) == os.path.basename(source_path)`.
2. Validate that the full destination path does not exceed `PATH_MAX` for the destination filesystem (see source directory structure section).
3. Determine the staging dir for `/mnt/music/rips/foo.flac` (same device as source).
   - Preferred: `/mnt/music/.bes_cache/move_staging/<operation_uuid>/foo.flac`
   - Fallback: `~/.bes/<device_hex>/move_staging/<operation_uuid>/foo.flac`
4. `os.rename(src, staging_path)` — atomic on POSIX for same-filesystem moves; the file disappears from its original location immediately.
5. Record the operation in the SQLite database with status `staging_done`.
6. Queue the (staging_path → dst) copy to the worker thread.
7. When the copy completes, delete the staging file and its UUID directory; mark status `done`.

The UUID directory per operation ensures two concurrent moves of files with the same basename don't collide in staging.  The basename is always the original filename — the UUID is the directory, never part of the filename itself.

---

## Database schema

The caller supplies the database path to the `bf_file_mover` constructor.  `bf_file_mover_database_locator` provides a conventional default (`~/.bes/move/move.sqlite`) but the caller is free to use any path — a project-specific location, a test-specific temp path, etc.

The staging files live on the source device (required for the atomic `os.rename`), but the database does not need to.  Keeping it in a stable user-accessible location means it is always accessible regardless of which devices are mounted, `bf_file_mover` holds a single connection, and querying all pending or paused operations across all sources requires no device enumeration.  The `staging_path` column is sufficient to locate any staging file on disk.

`bf_volume_locator` is therefore used only to find the staging directory, not the database.

```sql
create table move_operations_v1 (
  operation_id          text    primary key not null,   -- uuid
  source_path           text    not null,
  staging_path          text    not null,
  destination_path      text    not null,
  destination_device_id text,                           -- st_dev at submit time; NULL if dst dir did not exist yet
  status                text    not null,               -- see bf_file_mover_status
  submitted_at          integer not null,               -- unix epoch
  staged_at             integer,
  copy_started_at       integer,
  paused_at             integer,
  completed_at          integer,
  error_message         text
)
```

Indices: `status`, `submitted_at`.

Status transitions:

```
pending → staging_done → copying → done
                       → paused  → copying → done
                                           → failed
                       → failed
```

On restart, any operation in `copying` state is resumed (staging file present) or marked `failed` (staging file gone).  Operations in `paused` are re-checked on `start_worker()`.

---

## Paused operations — destination unavailable

Some destinations are removable volumes (USB drives, SD cards, network shares) that may not be present when the worker tries to copy.  Rather than failing these immediately, the worker enters a `paused` state and waits for the volume to return.

`paused` means: the staging file is safe, the destination path is known, but the destination filesystem is not currently reachable.  `destination_device_id` (recorded at submit time if the destination directory already existed) lets us detect when that specific device reappears rather than just any path becoming writable.

### How the worker detects a missing destination

Before starting a copy the worker calls `os.path.exists(destination_dir)`.  If that fails (path not present, or `os.stat` raises `OSError` with `ENOENT`/`EIO`/`ESTALE`) the operation is marked `paused` and skipped for that loop iteration.  The worker does not spin-wait — it continues processing other items in the queue and revisits `paused` operations only when a resume check is triggered (see below).

### Triggering a re-check

Two mechanisms, both explicit:

**1. On startup (boot / application launch)**

When `start_worker()` is called it always runs a resume scan before entering the main loop.  Any operation in `paused` state has its destination path re-tested.  If the path is now reachable, the operation is re-queued as `staging_done` so the copy will proceed.  This handles the common case of "plug in USB, launch app."

**2. Manual trigger**

```python
mover.resume_paused()  # test all paused operations right now; re-queues any whose destination is reachable
```

The caller decides when to call this — e.g. in response to a platform volume-mount notification, a CLI command, or a UI button.  No automatic polling timer is started by the framework.

### Platform volume-mount notifications (future)

macOS exposes `DiskArbitration` callbacks; Linux has `udev`; both can call `mover.resume_paused()` when a new volume mounts.  Wiring this up is outside scope for the initial implementation but the API is designed so a thin platform shim can do it with one call.

### Error handling for paused operations

| Condition | Behaviour |
|---|---|
| Destination unreachable at copy start | Status → `paused`; staging file preserved |
| Destination reappears with different device id | Treat as new unknown device; re-check path writability; proceed if writable |
| Operation has been `paused` for > TTL (see staging cleanup) | Status → `expired` by `vacuum_staging()`; staging file deleted |

---

## Orphan warnings

An orphan is a file present in the staging directory tree that has no corresponding database record in an active state (`pending`, `staging_done`, `copying`, or `paused`).  This can happen if the database is lost, corrupted, or manually deleted, or if a staging file was left behind by a bug.

### When orphans are detected

The startup recovery scan inside `start_worker()` walks the entire staging directory tree after processing known operations.  Any file found with no matching `operation_id` directory in the database is logged as a warning:

```
WARNING: orphaned staging file: /mnt/music/.bes_cache/move_staging/a3f9.../foo.flac (42 MB, no database record)
```

The warning includes the path and size so the user can assess the impact without having to go look manually.  Orphans are **not** deleted automatically — they are surfaced and left alone.

### Manual inspection

```python
orphans = mover.list_orphans()   # → list of absolute paths
```

The caller decides what to do: log them, show them in a UI, pass them to `vacuum_staging()`, or leave them.

### Why not auto-delete

An orphaned staging file is the original source file after its `os.rename` — deleting it silently is data loss.  Warning and leaving it intact is the only safe default.

---

## Source directory structure

### The problem

The staging path uses `<operation_uuid>/basename`, which is safe (no collisions, no path length issues) but opaque — if you open the staging directory manually you see a flat list of UUIDs with no indication of where files came from.

Preserving the full relative source path in staging would be human-readable, but introduces two problems:

1. **Basename collision.** If the same file is queued twice (or two files with the same name from the same source directory), both would map to the same staging path and the second `os.rename` would overwrite the first.
2. **PATH_MAX.** macOS enforces 1024 bytes for a full path; Linux is 4096.  A deeply nested source tree under a staging root that is itself not at the volume root can easily exceed this.  Example: volume root is not `/` but `/Volumes/BigDisk/`, staging is under `.bes_cache/`, and the source is `Music/By Artist/Very Long Name/Remastered Edition/Disc 1/track01.flac` — the combined path is long before even counting the staging prefix.

### Decision: keep `<operation_uuid>/basename` in staging

The staging area is a transient working space, not a human-browsable archive.  The database is the index.  `list_orphans()` and `list_operations()` provide programmatic visibility without requiring the filesystem layout to carry meaning.

The database already records `source_path` and `destination_path` for every operation, so the association between UUID directory and original file is always recoverable.

### Destination path length validation

Even though the staging path is safe, the destination path is caller-supplied and can be arbitrarily long.  `move()` validates the destination path length before staging the source:

```python
limit = 1024 if host.is_macos() else 4096
if len(destination_path.encode('utf-8')) >= limit:
    raise ValueError(f'destination path exceeds PATH_MAX ({limit}): {destination_path}')
```

This fails before the source is touched, so no data is moved if the destination path is invalid.

### Moving a directory tree (future)

A higher-level `move_tree(source_root, destination_root)` that walks a source directory and enqueues one `move()` per file, computing `destination_path = os.path.join(destination_root, os.path.relpath(source_path, source_root))`, is a natural extension.  The basename constraint is automatically satisfied because `relpath` preserves it.  Path length validation catches any cases where the destination root is deep enough to push individual files over the limit.  This is out of scope for the initial implementation.

---

## Copy implementation

### Chunk sizes

| Filesystem | Optimal chunk | Rationale |
|---|---|---|
| macOS APFS | 1 MiB (1,048,576 bytes) | APFS clone unit; aligns to APFS block size |
| Linux ext4 | 4 MiB | Matches typical readahead window |
| Linux ZFS | 4 MiB | Matches default record size |
| Windows NTFS | 1 MiB | Adequate; not a performance target |

In practice, a single default of **4 MiB** works well across all targets.  Same-device moves never reach the copy loop at all — they use `os.rename` directly from staging to destination.

```python
# Pseudo-logic in the worker
if same_device(staging_path, destination_path):
    os.rename(staging_path, destination_path)
else:
    for chunk in _read_chunks(staging_path, chunk_size):
        dst_fd.write(chunk)
    os.fsync(dst_fd.fileno())
    os.remove(staging_path)
os.rmdir(staging_uuid_dir)   # always: uuid dir is now empty
```

After the copy, verify file size matches source.  Optionally checksum-verify (off by default, configurable in `bf_file_mover_options`).

---

## Worker thread vs. worker process

### Thread

**Pros:**
- Shares the same SQLite database connection pool and in-process state — simpler coordination.
- Lower startup overhead; sub-millisecond to start/stop.
- Easy to pass Python objects (queue, callbacks) across the boundary.
- Adequate for I/O-bound work: the GIL releases during `read`/`write` syscalls.

**Cons:**
- A crash in the copy loop (e.g. corrupt file triggering a kernel panic path) can take down the host process.
- Python GIL means true CPU parallelism is impossible — irrelevant here since the bottleneck is I/O, not CPU.
- A misbehaving copy loop can starve other threads if the GIL is held in tight native code.

### Process

**Pros:**
- Full isolation — a crash in the worker does not affect the host process.
- Separate address space prevents accidental shared-state mutation.
- Scales to multiple CPU cores if copy logic ever becomes CPU-bound (e.g. encryption).

**Cons:**
- `multiprocessing` startup is expensive (~100 ms) and heavyweight.
- Passing work items requires pickling or IPC (queue, pipe, or shared memory).
- SQLite requires careful cross-process locking (WAL mode helps, but it's an extra constraint).
- Harder to propagate exceptions and progress back to the caller.

### Recommendation: thread

The workload is pure I/O.  The simplicity of in-process coordination, shared SQLite connection, and cheap start/stop outweighs the isolation benefit.  If a future use case requires isolation (e.g. running many concurrent copies of large files with separate crash domains), revisit.

---

## Worker thread lifecycle

The worker is **not** started automatically.  The application owns its lifecycle explicitly:

```python
mover = bf_file_mover(database_path, options)
mover.start_worker()          # starts the background thread; runs startup recovery scan first
mover.move(src, dst)          # enqueues an operation; returns operation_id
status = mover.status(operation_id)
mover.resume_paused()         # re-check all paused operations right now; call anytime
mover.stop_worker(wait=True)  # graceful: finishes in-flight copy, then exits
mover.stop_worker(wait=False) # immediate: abandons in-flight copy; staging file remains
```

The thread loop:
1. On `start_worker()`: run startup recovery scan before entering the main loop (see decisions).
2. Block on an internal `queue.Queue` with a configurable timeout.
3. On item: run the copy, update database, emit callbacks if configured.
4. On timeout with no items and a shutdown event set: exit.
5. On unhandled exception: mark the operation `failed`, log, continue (do not crash the thread).

---

## Public API sketch

```python
class bf_file_mover_options:
  chunk_size: int = 4 * 1024 * 1024
  verify_checksum_after_copy: bool = False
  on_progress: callable = None   # on_progress(operation_id, bytes_copied, total_bytes)
  on_complete: callable = None   # on_complete(operation_id)
  on_pause: callable = None      # on_pause(operation_id) — destination went missing

class bf_file_mover:
  def __init__(self, database_path, options=None): ...

  def start_worker(self): ...      # runs startup recovery scan, then enters loop
  def stop_worker(self, wait=True): ...

  # Enqueue a move; returns operation_id immediately.
  # Raises if worker is not running.
  def move(self, source_path, destination_path) -> str: ...

  def status(self, operation_id) -> bf_file_mover_status: ...
  def operation(self, operation_id) -> bf_file_mover_operation: ...

  # Returns all operations in a given status, optionally filtered by date range.
  def list_operations(self, status=None, since=None) -> list[bf_file_mover_operation]: ...

  # Re-check all paused operations; re-queues any whose destination is now reachable.
  def resume_paused(self): ...

  # Return paths of staging files with no active database record.
  def list_orphans(self) -> list[str]: ...

  # Retry a failed operation (re-queues; staging file must still exist).
  def retry(self, operation_id): ...

  # Remove staging files for failed/paused operations older than minimum_age_days.
  def vacuum_staging(self, minimum_age_days): ...
```

---

## Error handling

| Failure point | Behaviour |
|---|---|
| `os.rename` to staging fails | Operation marked `failed` immediately; source file untouched |
| Source device full (staging) | Same as above |
| Destination unreachable at copy start | Status → `paused`; staging file preserved; `on_pause` callback fired |
| Destination write error mid-copy | Status → `failed`; partial destination file deleted; staging file and UUID dir preserved for retry |
| Staging file missing on retry or recovery scan | Status → `failed`; UUID dir removed if empty |
| `paused` operation staging file missing on vacuum | Status → `expired`; UUID dir removed if empty |
| `paused` operation older than TTL | Status → `expired` by `vacuum_staging()`; staging file and UUID dir deleted |
| Database write error | Logged; copy continues; status update retried on next loop tick |

---

## Decisions

### 1. Recovery scan at startup

**Decision: automatic, always, inside `start_worker()`.**

`start_worker()` scans the database for all operations in `copying` or `paused` state before entering the main loop:

- `copying` with staging file present → re-queue as `staging_done` (resume the copy).
- `copying` with staging file missing → mark `failed` (unrecoverable; file is gone).
- `paused` with destination now reachable → re-queue as `staging_done`.
- `paused` with destination still unreachable → leave as `paused`.

This is automatic because there is no sensible reason to skip it — the staging file is the source of truth.  If the destination has changed between runs that is fine: the copy will simply write to the new path.  The scan runs synchronously before the first queue item is processed, so by the time the first `move()` call returns, all recoverable prior work is already re-queued.

---

### 2. Single worker thread regardless of device

**Decision: one worker thread total, no per-device splitting.**

The workload is entirely I/O-bound.  Python's GIL releases during `read` and `write` syscalls, so multiple threads could run real I/O in parallel — but the bottleneck is device throughput, not CPU.  Multiple threads writing to the same physical device (USB drive, spinning disk) would compete for the same hardware queue and reduce throughput compared to sequential access.

"Per-device worker" would mean one thread per *destination* device.  The source device matters less because the staging rename is near-instant; the long operation is the copy to the destination.  A separate thread per destination would be useful if copies to multiple destinations could genuinely run in parallel without saturating any one device — e.g. two USB drives connected simultaneously.  This is a real case but adds significant complexity (thread pool management, per-device queues, database contention).

**For now: one worker, one queue, sequential copies.**  If profiling shows a clear bottleneck from serialised copies to independent devices, add a `max_workers` option to `bf_file_mover_options` that spins up N threads each pulling from the same queue.  N=1 is the default and the simple case.

---

### 3. Progress callbacks

**Decision: `on_progress(operation_id, bytes_copied, total_bytes)` in options.**

The callback fires from the worker thread after each chunk write.  The caller is responsible for thread safety if it updates UI state.  The interval between callbacks is determined by `chunk_size` (default 4 MiB), so for a 400 MiB file there will be ~100 callbacks — fine for progress bars, not so fine for logging.  If the caller wants coarser granularity it can throttle on its own side (e.g. only update the UI if `bytes_copied - last_reported > 20 MiB`).

`total_bytes` is the file size at the time the copy starts (from `os.stat` on the staging file).  If somehow the staging file changes size mid-copy (it shouldn't) `total_bytes` will be stale — that is acceptable.

`on_complete(operation_id)` fires once when status transitions to `done`.  `on_pause(operation_id)` fires when the worker detects the destination is missing and transitions to `paused`.

---

### 4. Staging cleanup TTL

**What it is:** when a copy fails or a destination never comes back, the staging file (the `os.rename`'d source) stays on disk indefinitely.  Without cleanup, these orphaned files accumulate and quietly consume disk space on the source device, with no visibility to the user.

**Decision: explicit `vacuum_staging(minimum_age_days)` method; no automatic timer, no default age.**

`vacuum_staging(minimum_age_days)` does:
1. Query the database for all operations with status `failed` or `paused` where the relevant timestamp is older than `minimum_age_days`.
2. For each: check the staging file exists, delete it, mark the operation `expired` in the database.
3. Operations marked `expired` are kept in the database for audit but are no longer actionable.

The caller decides both when to run it and what age threshold to use.  There is no default because the right value depends on context — an application moving files to a regularly-connected USB drive might use 7 days; one moving to a rarely-connected archive drive might use 180.

A `paused` operation is never promoted to `expired` by the TTL scan if its staging file is still intact — only `failed` operations, or `paused` operations whose staging file has already gone missing, are candidates.  This ensures that "forgotten" USB drives don't silently lose their pending copies.

---

### 5. No `clonefile` needed

`clonefile(2)` saves time over a `read`/`write` loop when you need to copy a file while keeping the source intact.  A move does not keep the source, so the same-device case is already handled by `os.rename` — which is atomic, instant, and requires no platform-specific code.  The chunk copy loop is only reached when staging and destination are on different devices, at which point `clonefile` is not applicable anyway.  Nothing to add here.

---

## Unit test coverage

All tests live in `tests/lib/bes/files/move/`.  Each test creates a fresh temp directory and a fresh database at a temp path — no shared state between tests.  Tests that need cross-device behaviour use a RAM-backed tmpfs mount (Linux) or a disk image (macOS) to simulate a second device; helpers for this live in a shared `_test_device_fixture` module.

### `test_bf_file_mover_database.py` — persistence layer in isolation

| Test | What it covers |
|---|---|
| `test_create_and_schema_version` | Database is created, WAL mode is on, schema version is correct |
| `test_insert_and_retrieve_operation` | Insert a record, retrieve it by operation_id, all fields match |
| `test_update_status` | Status transition persisted correctly |
| `test_list_by_status` | `list_operations(status=...)` returns only matching rows |
| `test_list_since` | `list_operations(since=...)` respects the timestamp filter |

### `test_bf_file_mover.py` — full behaviour

**Constructor and setup**

| Test | What it covers |
|---|---|
| `test_init_creates_database_file` | Constructor creates the `.sqlite` file at the given path |
| `test_init_creates_database_parent_dirs` | Parent directories of the database path are created if absent |
| `test_move_raises_if_worker_not_running` | `move()` before `start_worker()` raises `RuntimeError` |

**Validation**

| Test | What it covers |
|---|---|
| `test_move_raises_on_mismatched_basename` | `move('a/foo.flac', 'b/bar.flac')` raises `ValueError` |
| `test_move_raises_on_destination_path_too_long` | Path at or beyond `PATH_MAX` raises `ValueError` before source is touched |
| `test_move_raises_on_destination_path_too_long_source_untouched` | Source file still exists after the above rejection |

**Staging**

| Test | What it covers |
|---|---|
| `test_move_stages_file_immediately` | After `move()` returns, source path is gone and staging file exists |
| `test_staging_creates_uuid_directory` | Staging area contains a UUID-named subdirectory |
| `test_staging_preserves_basename` | File inside UUID dir has the original basename |
| `test_staging_two_same_basename_files_no_collision` | Two files named `foo.flac` from different dirs each get separate UUID dirs |
| `test_staging_prefers_volume_root` | When volume root is writable, staging goes to `<volume_root>/.bes_cache/move_staging/` |
| `test_staging_falls_back_to_home` | When volume root is not writable, staging goes to `~/.bes/<device_hex>/move_staging/` |

**Happy path — same device**

| Test | What it covers |
|---|---|
| `test_move_same_device_completes` | File appears at destination with correct contents |
| `test_move_same_device_uses_rename` | `os.rename` path taken (no chunk loop); verified by checking no intermediate copy exists |
| `test_move_same_device_uuid_dir_removed` | UUID dir is gone after completion |
| `test_move_same_device_status_done` | Final status is `done` |

**Happy path — cross device**

| Test | What it covers |
|---|---|
| `test_move_cross_device_completes` | File appears at destination with correct contents |
| `test_move_cross_device_staging_file_removed` | Staging file deleted after copy |
| `test_move_cross_device_uuid_dir_removed` | UUID dir deleted after copy |
| `test_move_cross_device_status_transitions` | Status goes `staging_done` → `copying` → `done` in database |
| `test_move_cross_device_file_size_verified` | Status `done` only after size check passes |
| `test_checksum_verification_passes` | With `verify_checksum_after_copy=True`, matching checksums → `done` |
| `test_checksum_verification_fails` | Mismatched checksum → `failed`; staging preserved; partial destination deleted |

**Callbacks**

| Test | What it covers |
|---|---|
| `test_on_complete_fires` | `on_complete(operation_id)` called exactly once on success |
| `test_on_progress_fires` | `on_progress(operation_id, bytes_copied, total_bytes)` called at least once per copy |
| `test_on_progress_total_bytes_correct` | `total_bytes` matches `os.stat` size of the source file |
| `test_on_progress_final_call_equals_total` | Last `on_progress` call has `bytes_copied == total_bytes` |
| `test_on_pause_fires` | `on_pause(operation_id)` called when destination is unreachable |

**Worker lifecycle**

| Test | What it covers |
|---|---|
| `test_start_worker_starts_thread` | Thread is alive after `start_worker()` |
| `test_stop_worker_wait_true` | `stop_worker(wait=True)` returns only after in-flight copy finishes |
| `test_stop_worker_wait_false` | `stop_worker(wait=False)` returns immediately; staging file remains |
| `test_double_start_raises` | Second `start_worker()` raises `RuntimeError` |
| `test_worker_exception_does_not_crash_thread` | Injected exception in copy loop marks op `failed` and thread keeps running |

**Paused — destination unavailable**

| Test | What it covers |
|---|---|
| `test_pauses_when_destination_dir_missing` | Destination directory does not exist → status `paused` |
| `test_pauses_on_eio` | `os.stat` raises `EIO` on destination → status `paused` |
| `test_destination_device_id_recorded_when_dir_exists` | `destination_device_id` populated at submit time |
| `test_destination_device_id_null_when_dir_missing` | `destination_device_id` is `NULL` when dir absent at submit time |
| `test_resume_paused_requeues_when_available` | After destination dir is created, `resume_paused()` re-queues the operation |
| `test_resume_paused_leaves_paused_when_still_missing` | `resume_paused()` with destination still absent changes nothing |
| `test_resume_paused_different_device_id_proceeds_if_writable` | Destination reappears with different `st_dev`, path is writable → proceeds |
| `test_start_worker_resumes_paused_on_startup` | `paused` op present in db, destination now reachable → re-queued inside `start_worker()` |

**Recovery scan at startup**

| Test | What it covers |
|---|---|
| `test_recovery_resumes_interrupted_copy` | Op in `copying` state, staging file present → re-queued, copy completes |
| `test_recovery_fails_interrupted_copy_missing_staging` | Op in `copying` state, staging file gone → status → `failed` |
| `test_recovery_runs_before_first_move` | New `move()` call is not processed until recovery scan finishes |

**Orphans**

| Test | What it covers |
|---|---|
| `test_list_orphans_finds_untracked_file` | Staging file with no db record appears in `list_orphans()` |
| `test_list_orphans_empty_when_all_tracked` | No orphans when every staging file has an active db record |
| `test_list_orphans_excludes_done_operations` | Completed ops whose staging files are already deleted are not orphans |
| `test_orphan_not_deleted_automatically` | Orphan file still on disk after `start_worker()` |
| `test_start_worker_logs_orphan_warning` | Log contains warning with path and size for each orphan |

**`vacuum_staging`**

| Test | What it covers |
|---|---|
| `test_vacuum_removes_old_failed_staging_file` | `failed` op older than `minimum_age_days` → staging file deleted, UUID dir deleted, status `expired` |
| `test_vacuum_preserves_recent_failed` | `failed` op younger than `minimum_age_days` → untouched |
| `test_vacuum_removes_paused_with_missing_staging` | `paused` op, staging file already gone → status `expired`, UUID dir removed if empty |
| `test_vacuum_preserves_paused_with_intact_staging` | `paused` op, staging file still present → **not expired, not deleted** (key invariant: intact staging = recoverable move) |
| `test_vacuum_expired_records_remain_in_database` | After vacuum, `expired` records are still queryable |
| `test_vacuum_expired_not_retriable` | `retry()` on an `expired` operation raises `RuntimeError` |

**Error handling**

| Test | What it covers |
|---|---|
| `test_staging_rename_fails_source_untouched` | Simulated `os.rename` failure → source file still at original path, status `failed` |
| `test_mid_copy_failure_deletes_partial_destination` | Write error injected mid-copy → partial destination file deleted |
| `test_mid_copy_failure_preserves_staging_file` | Same scenario → staging file still present |
| `test_mid_copy_failure_preserves_uuid_dir` | Same scenario → UUID dir still present |
| `test_retry_requeues_with_staging_file` | `retry()` on `failed` op with staging present → re-queued, copy completes |
| `test_retry_raises_without_staging_file` | `retry()` on `failed` op with staging gone → raises `RuntimeError` |
| `test_database_write_error_logged` | Simulated db write failure → error logged, copy continues, status retried next tick |

**Concurrency**

| Test | What it covers |
|---|---|
| `test_multiple_files_queued_all_complete` | Queue 5 files, all reach `done` status |
| `test_same_basename_concurrent_no_collision` | Two simultaneous moves of `foo.flac` from different dirs both complete correctly |
