# bf_media_finder — Design and Requirements

## Overview

A standalone, testable component in `bes/files/media_finder/` that scans directories
for media files using mime detection, with no Qt or UI dependencies. Serves as the
engine that higher-level components (CLI, Qt UI) drive through callbacks.

---

## Current Behavior (Source of Truth for Extraction)

Describes what `rui_media_list` currently does that must be preserved and made testable.

### State Machine

```
IDLE → SCANNING → FILTERING → READY_QUICK → RESOLVING_SLOW → READY_SLOW
```

- **IDLE**: no directories configured or no files match
- **SCANNING**: `bf_file_scanner` is running in a btask worker, reporting file batches
- **FILTERING**: scan done, synchronous sort pass executing
- **READY_QUICK**: sort done, files visible; slow attributes not yet resolved
- **RESOLVING_SLOW**: one btask per file resolving resolution, duration
- **READY_SLOW**: all slow attributes resolved, final sort applied

Only the last sort and resolve are triggered when the active sort type is one of the
"slow" attributes. If the sort type is fast, READY_QUICK is terminal.

### Phase 1 — Scan

- Accepts one or more root directories and a set of media types (`image`, `video`).
- Uses `bf_file_scanner` in a btask worker.
- Respects `.bes_ignore` files to skip directories.
- Filters out files ending in `.part` and files whose basenames start with `._`.
- Skips files that no longer exist at add time.
- Reports progress in batches of 50 filenames via a status callback.
- Reports a final done callback with total count when the scan completes.
- Supports cancellation mid-scan; cancellation discards all accumulated results.
- If a scan is already in progress when a new scan is requested, the in-progress
  scan is cancelled before the new one starts.

### Phase 2 — Metadata Resolution ("slow resolve")

- Triggered automatically after READY_QUICK if the active sort type requires slow
  attributes, or manually when the sort type is changed to a slow sort.
- Dispatches one btask per file to resolve: `resolution`, `duration`.
- Reports per-file completion via a callback: (done_count, total_count).
- Reports a final done callback when all files are resolved.
- Debounces re-sort during resolution: re-sorts at most once per 250 ms while
  callbacks arrive, then does a final sort when all are done.
- Supports cancellation; in-flight resolve tasks are cancelled when a new scan
  starts or when `cancel` is called explicitly.
- Individual file resolve errors are swallowed silently (best-effort).

### Sort Types

**found_order** (default): files appear in emission order as the scan walks the
filesystem. No sort pass is applied.

Fast sort types (sortable immediately after scan):
- name, path, date (modification), size, kind (mime_type)

Slow sort types (require Phase 2 metadata resolution):
- resolution, width, height, aspect_ratio, duration, average_hash_v1

---

## Attribute Tier Model

File attributes fall into three cost tiers that drive the pipeline architecture.

### Tier 0 — Free (directory walk, `stat()`)

- path, basename, extension
- size (bytes)
- modification date

### Tier 1 — Cheap (magic bytes, head-of-file read)

Requires opening each file and reading a small header (< 512 bytes). The
`bf_mime_type_detector` fallback chain handles this.

On a fast SSD: ~0.05–0.15 ms per file. On platter: ~5–15 ms per file.

Attributes available at Tier 1:
- `mime_type` (e.g. `image/jpeg`, `video/mp4`)
- `media_type` (derived: `image` | `video` | `other`)

**Critical correctness property**: Tier 1 detects corrupted files that have a valid
extension but invalid content. Extension alone is never the acceptance gate — mime
type is authoritative.

### Tier 2 — Expensive (full file parse)

Requires reading substantial file content. Cost scales with file size.

**Tier 2a — header parse** (fast relative to 2b):
- `resolution` (image: reads IHDR/SOF0 marker; video: reads moov atom)
- `duration` (video container header)

**Tier 2b — full content decode** (medium-slow):
- `average_hash_v1` (perceptual hash — requires full image decode)

Under the new design, `mime_type` and `media_type` are resolved in Phase 1 (Tier 1),
not Phase 2. The current slow_btask resolved them together because mime_type was
needed there historically; it no longer is.

---

## Acceptance Criteria vs Sort Criteria

These are two orthogonal concepts that the current code conflates.

**Acceptance criteria** — does this file belong in the result set at all?
Determined entirely during Phase 1 using Tier 1 mime detection. Extension is ignored.
Corrupted files with valid extensions are rejected.

**Sort criteria** — how should accepted files be ordered?
Applied after acceptance. The scan phase is always the same regardless of sort type.
`found_order` means no sort pass runs at all.

---

## Revised State Machine

```
IDLE → SCANNING → READY_QUICK → RESOLVING_SLOW → READY_SLOW
```

The FILTERING state is collapsed into the SCANNING→READY_QUICK transition (sort is
synchronous and fast enough to not warrant a visible state).

- **SCANNING**: full Tier 0 + Tier 1 pass in a single btask. Files emitted only after
  mime verification. Progress reports two counters: `found` (accepted) and `scanned`
  (examined).
- **READY_QUICK**: all files have Tier 0 + Tier 1 attributes. If sort type is
  `found_order`, this state is terminal. For fast sort types a synchronous sort pass
  runs at transition time.
- **RESOLVING_SLOW**: only triggered if sort type requires Tier 2 (resolution, width,
  height, aspect_ratio, duration, average_hash_v1).
- **READY_SLOW**: Tier 2 resolved, final sort applied.

### Sort Tier Classification

**found_order** (default): emission order, no sort pass, READY_QUICK is terminal.

Fast (Tier 0 + 1, synchronous sort at READY_QUICK):
- name, path, date, size, kind (mime_type)

Slow (Tier 2a/2b, require RESOLVING_SLOW):
- resolution, width, height, aspect_ratio, duration (Tier 2a)
- average_hash_v1 (Tier 2b)

---

## Scan Progress Reporting

Two independent counters throughout the scan loop:

- **scanned**: total filesystem entries examined (monotonically increasing)
- **found**: files accepted (subset of scanned)

Progress message: `found {found}  scanned {scanned}` with no percentage.

---

## Mime Type Caching (Future — `bf_mime_xattr_cache`)

On SSD, on-the-fly magic byte detection is fast enough (~100 ms per 1,000 files) that
xattr caching adds no meaningful value. On platter disk, xattr caching saves real time
on repeated opens of the same large directory (100× faster than re-reading magic bytes).

The cache stores mime type as xattr `user.bf.mime_type` with `(size, mtime)` as the
invalidation key. No sha256 needed. Falls back gracefully if xattrs unavailable.

This is a future optimization; the scan always works correctly without it.

---

## Components

### `bf_media_file_entry`

Frozen dataclass. Fields: `root_dir`, `filename` (absolute), `size`, `mtime`,
`extension`, `mime_type`, `media_type`. `relative_filename` property computed from
the two. `__str__` returns `filename`. Registered with `check`.

### `bf_media_sort_type`

Enum with `is_slow` property. Fast: `FOUND_ORDER`, `NAME`, `PATH`, `DATE`, `SIZE`,
`KIND`. Slow: `RESOLUTION`, `WIDTH`, `HEIGHT`, `ASPECT_RATIO`, `DURATION`,
`AVERAGE_HASH`. Slow types raise `NotImplementedError` until Tier 2 is implemented.

### `bf_media_finder_state`

`IDLE`, `SCANNING`, `READY_QUICK`, `RESOLVING_SLOW`, `READY_SLOW`.

### `bf_media_finder_options`

`bcli_options` subclass. Fields: `media_types` (frozenset), `sort_type`,
`ignore_file`, `case_sensitive`.

### `bf_media_finder_callbacks`

Dataclass of optional callables: `on_scan_progress(found, scanned)`,
`on_scan_done(entries)`, `on_cancel()`, `on_state_changed(state)`, `on_error(exc)`.

### `bf_media_finder`

Owns `btask_main_thread_runner_py` and `btask_result_collector_py`. Processor is
injected (CLI creates its own; Qt app injects shared one).

`scan(root_dirs, options=None, callbacks=None)` — starts the scan.
`cancel()` — defers `processor.cancel()` to a daemon thread to avoid re-entrant
deadlock when called from a status callback.
`run()` — blocks until scan completes or is cancelled.

Slow sort types route `NotImplementedError` through `on_error` rather than raising
out of `run()`.

### `bf_media_scan_task`

btask worker. Walks dirs via `bf_file_scanner`, applies `.part` / `._` filename
filters, detects mime via `bf_mime_type_detector` (extension ignored), streams
`bf_media_scan_status` batches of 50. Uses `raise_cancelled_if_needed` for proper
CANCELLED result state.

---

## Requirements

### R1 — Component Location and Dependencies

- Lives in `bes/files/media_finder/`.
- No dependency on Qt, rapp, rui, or bav.
- All callbacks are plain Python callables, not Qt signals.

### R2 — Scan Phase

- Accepts one or more root directory paths and a set of requested media types.
- Delegates directory traversal to `bf_file_scanner`.
- Supports optional ignore filename (`.bes_ignore`).
- Applies built-in filename filters (`.part` suffix, `._` basename prefix).
- Performs Tier 1 mime detection inline; emits only files whose `media_type` matches
  requested types. Corrupted files silently excluded.
- Emits `bf_media_file_entry` objects with Tier 0 + Tier 1 attributes.
- Reports `on_scan_progress(found, scanned)` and `on_scan_done(entries)`.
- Supports cancellation; no callbacks fire after cancellation.

### R3 — Metadata Resolution Phase (Tier 2, deferred)

- Triggered only when sort type requires Tier 2 attributes.
- `mime_type` and `media_type` are not resolved here — available from scan phase.
- Dispatches one btask per file for the specific attributes needed.
- Resolution/duration via direct header parse (Tier 2a, no sha256).
- `average_hash_v1` via full image decode (Tier 2b).
- Reports `on_resolve_progress(done, total)` and `on_resolve_done()`.
- Debounces intermediate re-sort (default 250 ms).

### R4 — State Machine

- Exposes discrete state: IDLE, SCANNING, READY_QUICK, RESOLVING_SLOW, READY_SLOW.
- Reports transitions via `on_state_changed(state)`.

### R5 — Cancellation and Reset

- `cancel()` cancels all in-progress tasks and transitions to IDLE.
- Component is ready for a new scan immediately after cancel.

### R6 — CLI

- `best2.py media find <dir> [options]`
- Flags: `--media-type`, `--sort`, `--ignore-file`, `--case-sensitive`,
  `--verbose`/`-v`, `--count`
- Progress to stderr; filenames to stdout (pipeable).
- SIGINT → cancel → exit 1.

### R7 — Unit Tests

- `bf_media_file_entry`: fields, frozen, relative_filename, check registration.
- `bf_media_sort_type`: fast/slow classification, parse, parse invalid.
- `bf_media_finder_options`: defaults, all fields, check registration.
- `bf_media_finder`: scan images/videos/all/empty; `.part` and `._` exclusion;
  corrupted file excluded; mime beats extension; non-standard extension found;
  entry fields populated; relative_filename; multiple roots; state transitions;
  done fired; progress counter validity and monotonicity; cancel mid-scan;
  second scan after cancel; sort name/size/date; slow sort routes to on_error.

---

## Future Work

### F1 — File System Monitoring

Watch root directories for changes using OS-native APIs (FSEvents/inotify).
New files via same `on_scan_batch` callback. Deleted files via `on_files_removed`.
Off by default, activatable after initial scan.

### F2 — Metadata Extensibility

Additional attributes (GPS, color profile, audio channels) addable by registering
a resolver per mime type without changing the core component.

### F3 — Result Persistence and Warm Start

Optionally persist the scanned file list so the initial display is instant on
re-open while a background scan detects changes.

### F4 — xattr Mime Cache as Default

Enable `bf_mime_xattr_cache` by default on macOS/Linux for platter-disk performance.
Consider extending to Tier 2 attributes (resolution, duration) using same
(size, mtime) invalidation key.
