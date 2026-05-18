# bfile-sync progress display — proposal

---

## Comments on requirements

Before the design, a few observations about the requirements that affect choices below.

### ETA accuracy requires bytes, not files

Large video files vary wildly in size (1 GB vs 50 GB). ETA based on file count is
nearly useless. ETA must be based on bytes: total bytes are known upfront from
`_collect_files`, elapsed real time gives a byte rate, remaining bytes / rate gives
the ETA. `time_util.format_eta(seconds)` is the right call.

### Skipped files and ETA

Skipped files (same checksum on NAS) complete in ~1–4 seconds (SSH round-trip for
`sha256sum`). They contribute **zero bytes** to `bytes_done`, so a byte-rate ETA
automatically handles them — the clock ticks, no bytes move, ETA shrinks only as
bytes accumulate. No special case needed.

### ETA bootstrap problem — first file

Until at least one file completes (or partial rsync progress arrives), there is no
rate to divide by. Show `ETA --:--` until a rate is established. The first transfer
unlocks a meaningful ETA.

### Pre-transfer work adds latency the user can see

Each file starts with an SSH `sha256sum` call (can be seconds for large files). During
this time the user sees the filename printed but nothing happening. The `...` indicator
on line 1 (compact) or the wait between line 1 and line 2 (verbose) covers this. No
additional design needed, but it is the reason line 1 must appear *before* the work
starts, not after.

### Two-line verbose vs one-line compact — they differ structurally

Verbose mode scrolls: both lines persist in the terminal. Compact mode overwrites:
line 1 (filename with `...`) is replaced in-place by the status line when the file
finishes. The morph is a `\r` overwrite, not a two-line layout. This means compact
mode shows only one line per file in the scrollback.

---

## Open issues and resolutions

1. **ETA after a retry**
   After a network failure the sync loop sleeps `retry_wait_seconds`. Including sleep
   time in elapsed tanks the byte rate and inflates ETA.
   **Resolution**: shift `start_time` forward by the sleep duration so elapsed only
   counts working time. `pause_clock()` records `pause_start = time.time()` before
   sleep; `resume_clock()` does `start_time += time.time() - pause_start` after.
   No extra state beyond one float.

2. **Rename case in compact mode**
   When destination exists with different content the file is transferred to a
   content-hash-suffixed name. It was unclear whether to show one status token or two.
   **Resolution**: use `RENAME` as the single status token. Bytes still accumulate in
   `bytes_done` (it is a real transfer). The accounting line is identical to a normal
   transfer. No special-casing required.

3. **Log file and `\r` lines**
   Intermediate `\r`-overwritten lines must not reach the log file.
   **Resolution**: `begin_file` writes only to `sys.stdout`. `finish_file` writes the
   finalized status line to both `sys.stdout` (with `\n`) and to `log_fh` (with a
   timestamp prefix added for the log). The tracker owns this split; `_emit` for
   session-level events is updated the same way: no timestamp on stdout, timestamp in
   the log file.

4. **Terminal width and long paths**
   Deep paths can wrap past 80 columns.
   **Resolution**: do nothing for now — wrapping is acceptable. Add
   `--max-path-width N` later if it becomes a real problem.

5. **Compact mode needs line-clearing**
   `\r` alone leaves stale characters when a shorter string follows a longer one.
   **Resolution**: use `\033[2K\r` (erase entire line, return to column 0) before
   every compact write. Unix-only for now per the stated constraint; works in Windows
   Terminal too if that ever matters.

6. **Spinner without a background thread**
   A cycling spinner needs periodic triggers — nothing fires mid-transfer without
   rsync progress callbacks.
   **Resolution**: `...` is static for now. When the shelved rsync progress work
   lands, `_on_rsync_progress(event)` fires per chunk and overwrites `...` with
   `93%  110 MB/s` naturally. No changes to the tracker interface are needed.

7. **`--compact` flag vs auto-detection**
   **Resolution**: auto-detect with `sys.stdout.isatty()` — compact on a TTY,
   verbose when redirected. `--compact` and `--verbose` flags override. These flags
   are mutually exclusive in argparse.

---

## Design

### State the progress tracker needs

```
total_files       int       — from len(_collect_files()) before the loop starts
total_bytes       int       — sum of path.getsize(e.absolute_filename) for all entries
current_index     int       — 1-based, incremented at the start of each file
bytes_done        int       — sum of file_size for completed transfers (skips add 0)
start_time        float     — time.time() at loop start, paused during retry sleep
active_file_path  str       — relative path of the file currently being processed
```

### ETA calculation

```python
elapsed = time.time() - start_time   # seconds, excluding retry sleep
rate    = bytes_done / elapsed        # bytes/second; skip if elapsed == 0
eta_sec = (total_bytes - bytes_done) / rate if rate > 0 else None
eta_str = time_util.format_eta(eta_sec) if eta_sec is not None else '--:--'
```

### `bf_size.sizeof_fmt` for amounts

Use the existing `bf_size.sizeof_fmt` for all human-readable byte values:
`transferred 1.23 GB of 45.6 GB`.

---

## Verbose mode output

Printed as plain scrolling text. Each file produces three writes.

```
[1/10] good-movies/_something/lemon/v1.mp4
[1/10] SKIP       same checksum  0.0B / 45.2GiB  ETA --:--

[2/10] good-movies/_something/lemon/v2.mp4
[2/10] TRANSFER   1.23GiB / 45.2GiB  ETA 00:42

[3/10] good-movies/_something/lemon/v3.mp4
[3/10] RENAME     → v3-abc12345.mp4  2.45GiB / 45.2GiB  ETA 00:39

```

- Line 1 printed **before** the work starts (checksum lookup, transfer).
- Line 2 printed **after** the work completes; no duplicate path (line 1 still visible).
- Reason appears in line 2: `same checksum` for SKIP, `→ newname` for RENAME, nothing for TRANSFER.
- One blank line after each line 2.
- Status tokens: `SKIP`, `TRANSFER`, `RENAME`; dry-run variants `DRY-SKIP`, `DRY-XFER`, `DRY-RENAME`.
- No timestamps on stdout; log file prefixes each entry with a timestamp.
- Both lines go to the log file; blank separator also logged.

---

## Compact mode output (TTY)

One overwritable line per file. Uses ANSI `\033[2K\r` to erase and reposition.

**While the file is being processed** (checksum + transfer running):

```
[2/10] good-movies/_something/lemon/v2.mp4 ...
```

No newline — stays on the same terminal line until the file completes.

**When the file finishes**, overwrite with the status line and end with `\n` to
lock it in. The path is included in the final line so scrollback is self-contained
even though the `...` line was erased:

```
[1/10] SKIP       good-movies/_something/lemon/v1.mp4  same checksum  0.0B / 45.2GiB  ETA --:--
[2/10] TRANSFER   good-movies/_something/lemon/v2.mp4  1.23GiB / 45.2GiB  ETA 00:42
[3/10] RENAME     good-movies/_something/lemon/v3.mp4 → v3-abc12345.mp4  2.45GiB / 45.2GiB  ETA 00:39
```

- Path always present → no "mystery STATUS with no filename" in scrollback.
- `→ newname` appended to path for RENAME; `  reason` appended for SKIP.
- Only the finalized status line goes to the log file (no `...` line).

---

## Why path is in the compact status line but not the verbose status line

Compact mode erases the `begin_file` line when `finish_file` runs, so the path
would be lost from scrollback without it. Verbose mode keeps both lines, so the
path on line 1 is already frozen; repeating it on line 2 would be redundant.

---

## Future rsync progress hook

When the shelved rsync progress work lands, `_on_rsync_progress(event)` will be
called with `rsync_progress(bytes_done, percent, rate, elapsed)` per chunk.
In compact mode, that callback calls:

```python
sys.stdout.write(
  f'\033[2K\r[{i}/{n}] {rel_path}  {event.percent}%  {event.rate}  '
  f'{done} / {total}  ETA {eta}'
)
sys.stdout.flush()
```

This replaces the static `...` with live data, on the same line, with no other
changes to the architecture. The final status overwrite at completion is identical
to today.

---

## TTY detection and flag behaviour

```python
import sys

is_tty = sys.stdout.isatty()
```

| stdout     | default mode | `--compact` | `--verbose` |
|------------|-------------|-------------|-------------|
| terminal   | compact     | compact     | verbose     |
| redirected | verbose     | compact*    | verbose     |

\* compact on a redirected stream writes `\033[2K\r` sequences into the file —
acceptable if the user explicitly requested it, but warn in help text.

CLI flags added to `bf_rsync_file_sync_cli`:

```
--compact    Force one-line-per-file compact output (default on TTY)
--verbose    Force two-line-plus-blank verbose output (default when redirected)
```

---

## Retry pause — stop the rate clock

When the loop detects a failure and sleeps, stop the elapsed timer:

```python
pause_start = time.time()
time.sleep(self._retry_wait_seconds)
start_time += time.time() - pause_start   # shift start forward by sleep duration
```

This prevents the sleep from diluting the byte rate and inflating ETA.

---

## Implementation sketch

### New class: `bf_rsync_progress_tracker`

File: `lib/bes/files/rsync/bf_rsync_progress_tracker.py`

```python
class bf_rsync_progress_tracker:
  def __init__(self, entries, compact, log_fh=None):
    # total_files, total_bytes from entries
    # compact flag, log_fh for log file writes
    # start_time = time.time()
    # bytes_done = 0, current_index = 0

  def begin_file(self, entry):
    # increment current_index
    # print line 1 (verbose) or the ... line (compact)

  def finish_file(self, entry, status, file_size, is_transfer):
    # update bytes_done if is_transfer
    # compute ETA
    # print line 2 (verbose + blank) or overwrite status line (compact)
    # write to log_fh

  def pause_clock(self):
    # called before retry sleep

  def resume_clock(self):
    # called after retry sleep; shifts start_time
```

### Changes to `bf_rsync_file_sync`

- Construct `bf_rsync_progress_tracker` at the top of `_run_loop`, replacing direct
  `_emit` calls for per-file events.
- Pass `compact` from a new `self._compact` attribute set in `__init__`.
- Remove `_emit` calls for `SKIP`, `DELETED`, `VERIFIED`, `TRANSFER`, `RENAME` —
  these become `tracker.begin_file` / `tracker.finish_file` calls.
- Keep `_emit` for `SUMMARY`, `ERROR`, `RETRY`, `CLEANUP` — these are session-level
  events that don't fit the per-file two-line structure.
- Call `tracker.pause_clock()` / `tracker.resume_clock()` around `time.sleep`.

### Changes to `bf_rsync_file_sync_cli`

- Add `--compact` / `--verbose` flags.
- Determine effective mode (flag vs TTY detection).
- Pass `compact=` to `bf_rsync_file_sync.__init__`.

---

## What does NOT change

- `_emit` for session-level events (`SUMMARY`, `RETRY`, `CLEANUP`, `ERROR`).
- The retry loop logic and `_sync_one` internals.
- The log file for session-level events.
- `bf_rsync_command.call_command` (no progress) for the non-compact path — the
  rsync progress hook is wired in `_rsync`, not in `call_command`.

---

## SSH remote checksum progress

### Design

A standalone script `bin/bfile-checksum.py` implements the remote checksum. It
imports nothing from `bes` — plain Python 3 stdlib only — so it runs on any NAS
with Python 3 available. It can be run and tested locally without any SSH machinery:
`python3 bin/bfile-checksum.py /path/to/file`.

At session start, before the first file is processed, `bf_rsync_file_sync` copies
this script to `/tmp/bfile-checksum.py` on the NAS via SSH. Each subsequent
`_ssh_sha256` call invokes it as `python3 /tmp/bfile-checksum.py '/path/to/file'`
and streams its stdout through `execute.execute_with_progress()`.

---

### Output protocol

The script emits structured lines to stdout prefixed with the algorithm name so the
local parser can identify them and ignore any incidental Python runtime output.

```
sha256: PROGRESS: 1048576/21474836480
sha256: PROGRESS: 2097152/21474836480
...
sha256: PROGRESS: 21474836480/21474836480
sha256: CHECKSUM: e3b0c44298fc1c149afbf4c8996fb924...
```

Units are bytes. The local side derives percent as `bytes_done / total_bytes * 100`.
File-not-found:

```
sha256: MISSING
```

All other lines are silently ignored by the local parser.

---

### Chunk strategy

`chunk_size = max(file_size // 100, 1_048_576)` computed once from `os.path.getsize`
before the read loop. Every file produces exactly 100 `PROGRESS` lines regardless of
size. The display advances in 1% steps. For files smaller than 100 MB the 1 MB floor
means fewer events, but those files complete fast enough that coarser granularity
does not matter.

---

### Script delivery

The script is copied once per session using an SSH call that pipes the file content
via stdin to `cat > /tmp/bfile-checksum.py` on the NAS. No chmod needed — the
script is always invoked as `python3 /tmp/bfile-checksum.py`, never executed
directly, so `noexec` mounts on `/tmp` are not a problem.

The script is overwritten on every session start so version drift is impossible.
If the NAS `/tmp` is read-only or full the copy fails immediately with a clear
`bf_rsync_error` before any file work begins.

Piping via stdin requires `bssh_command.call_command` to accept and forward
`input_data` bytes to `popen()`. `popen()` already handles `input_data`; the gap
is threading it through `call_command`.

---

### Local consumption

`_ssh_sha256` changes from a blocking `bssh_command.call_command()` to a streaming
`execute.execute_with_progress()` call. The line parser recognises:

- `sha256: PROGRESS: N/M` → fires `progress_callback(bytes_done, total_bytes)`
- `sha256: CHECKSUM: hex` → captures the return value
- `sha256: MISSING` → return `None`
- anything else → ignored

`_ssh_sha256` gains an optional `progress_callback` parameter. Callers that pass
`None` get silent behaviour identical to today. `_sync_one` passes a callback only
when `_show_progress` is True, consistent with the gate used for rsync and local
checksum progress.

---

## Implementation plan

### Step 1 — `bin/bfile-checksum.py`

New file. Plain Python 3, no `bes` imports. Takes the file path as `sys.argv[1]`
and the algorithm as `sys.argv[2]` (default `sha256`). Reads in chunks of
`max(file_size // 100, 1_048_576)` bytes, prints `algo: PROGRESS: done/total` after
each chunk, prints `algo: CHECKSUM: hex` at the end, prints `algo: MISSING` if the
file does not exist.

### Step 2 — `bssh_command.call_command` gains `input_data`

Add an `input_data` parameter (bytes, default `None`) that is passed through to
`popen()`. When set, the subprocess stdin receives the bytes before stdout reading
begins. This is a small change: `popen()` already opens `stdin=PIPE` when
`input_data` is not None; the call_command wrapper just needs to write and close it.

### Step 3 — `bf_rsync_file_sync._install_remote_checksum_script`

New private method called once at the top of `run()` (before `_run_loop`). Reads
`bin/bfile-checksum.py` from the local filesystem relative to the installed package,
calls `bssh_command.call_command` with `input_data=` and remote command
`cat > /tmp/bfile-checksum.py`. Raises `bf_rsync_error` with a clear message on
failure.

### Step 4 — `_ssh_sha256` rewritten as streaming call

Replaces the current single `bssh_command.call_command()` call with
`execute.execute_with_progress()` using a line parser for the protocol above.
Gains an optional `progress_callback` parameter. The existing call signature and
return type (`str | None`) are preserved.

### Step 5 — `_sync_one` wires up the callback

After the `_update_status('chk_remote')` call, determines whether to pass a progress
callback to `_ssh_sha256` using the same `_show_progress` gate already used for
rsync and local checksum progress. The callback writes
`\r[N/M] size - basename  chk_remote  NN%` to the terminal.

### Step 6 — tests

- Unit tests for `bfile-checksum.py` directly (run it against temp files, verify
  protocol output).
- Unit tests for `_install_remote_checksum_script` (mock SSH call, verify
  `input_data` contains expected script content).
- Unit tests for the updated `_ssh_sha256` (mock `execute_with_progress`, verify
  parser handles PROGRESS / CHECKSUM / MISSING / garbage lines correctly).
- Existing `_ssh_sha256` callers pass `None` → behaviour unchanged (existing tests
  cover this implicitly).
