# bf_media_finder — Requirements

## Overview

Extract the scanning, metadata resolution, and preview orchestration logic currently
embedded in `rui_media_list` into a standalone, testable component that has no Qt or
UI dependencies. The component lives in `bes/files/media_finder/` and serves as the
engine that rui-layer components drive through callbacks. A companion abstract preview
provider interface, also in bes, allows preview generation to be plugged in without
pulling graphics or format-specific dependencies into bes.

---

## Current Behavior (Source of Truth for Extraction)

This section describes what `rui_media_list` currently does that must be preserved
and made testable.

### State Machine

The system moves through these states in order:

```
IDLE → SCANNING → FILTERING → READY_QUICK → RESOLVING_SLOW → READY_SLOW
```

- **IDLE**: no directories configured or no files match
- **SCANNING**: `bf_file_scanner` is running in a btask worker, reporting file batches
- **FILTERING**: scan done, synchronous sort pass executing
- **READY_QUICK**: sort done, files visible; slow attributes not yet resolved
- **RESOLVING_SLOW**: one btask per file resolving mime_type, resolution, duration
- **READY_SLOW**: all slow attributes resolved, final sort applied

Only the last sort and resolve are triggered when the active sort type is one of the
"slow" attributes. If the sort type is fast, READY_QUICK is terminal.

### Phase 1 — Scan

- Accepts one or more root directories and a set of media types (`image`, `video`).
- Uses `bf_file_scanner` (via `scan_btask`) in a btask worker.
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
- Dispatches one btask per file to resolve: `mime_type`, `resolution`, `duration`.
- Currently uses `bav_file_entry` to pull these attributes, which reads from the
  attribute cache (sha256-keyed file attributes stored on disk).
- Reports per-file completion via a callback: (done_count, total_count).
- Reports a final done callback when all files are resolved.
- Debounces re-sort during resolution: re-sorts at most once per 250 ms while
  callbacks arrive, then does a final sort when all are done.
- Supports cancellation; in-flight resolve tasks are cancelled when a new scan
  starts or when `cancel` is called explicitly.
- Individual file resolve errors are swallowed silently (best-effort).

### Phase 3 — Preview Loading

- After READY_QUICK, previews are loaded for viewport-visible items.
- Uses a 250 ms debounce timer; when it fires, previews are requested for all
  currently viewport-visible items (plus a ±10 item buffer).
- The timer is restarted whenever the scroll position changes or the widget is resized.
- When changing directories, all in-progress preview requests are cancelled.
- Previews are cached on disk keyed by sha256 checksum of the file.
- Before requesting async generation, the cached preview is checked; if present,
  it is applied immediately without going through the async path.
- If no preview and no cache hit, a placeholder default icon (image or video) is shown.
- Generated previews are applied to the item when the async callback fires.
- If the item has been removed from the list by the time the callback fires, the
  result is silently discarded.
- Preview options include: size (default 256), strategy (width), video face confidence,
  and a `no_faces` flag that disables face detection (current default: True for speed).

### Sort Types

**found_order** (default): files appear in emission order as the scan walks the
filesystem. No sort pass is applied. Progressive display with no re-ordering during
scan. Selecting any other sort type triggers a sort pass (fast: immediate after scan;
slow: after metadata resolution).

Fast sort types (no resolve needed, sortable immediately after scan):
- name, name_lowercase, path, path_lowercase, date (modification), size,
  is_favorite, is_tagged, random, none, **kind** (mime_type — see note below)

Slow sort types (require Phase 2 metadata resolution):
- resolution, width, height, aspect_ratio, duration, average_hash_v1

Note: `kind` sorts by `mime_type`. Since mime_type is resolved inline during Phase 1
scan (Tier 1 magic byte detection), `kind` is a fast sort type under the new design
even though it is currently classified as slow.

### File-to-Item Deduplication

- A `filename → item` map prevents the same file from being added twice.
- When the list is cleared, this map is cleared.

---

## Attribute Tier Model

The key insight driving the new design is that file attributes fall into three cost tiers
that should drive the pipeline architecture. Mixing them into a single "slow resolve" phase
(as the current code does) is wasteful and the source of the UI wedging on large directories.

### Tier 0 — Free (directory walk, `stat()`)

Available from the directory traversal itself. No file opens required.

- path, basename, extension
- size (bytes)
- modification date
- file type (regular file vs symlink etc.)

### Tier 1 — Cheap (magic bytes, head-of-file read)

Requires opening each file and reading a small header (typically < 512 bytes, never more
than a few KB). The `bf_mime_type_detector` fallback chain handles this today:
- `_bf_mime_type_detector_cheesy`: reads magic bytes inline, pure Python, no library
- `puremagic`: reads magic bytes via library, more complete coverage
- `file` exe: spawns process — expensive, only falls back here

On a fast SSD, reading the magic header for 1,000 files costs roughly **50–150 ms total**
(~0.05–0.15 ms per file at 4K random read latency). On a platter disk it rises to
**5–15 seconds** (5–15 ms per seek+read). Both are acceptable: SSD is imperceptible,
platter is tolerable per the stated requirements.

Attributes available at Tier 1:
- `mime_type` (e.g. `image/jpeg`, `video/mp4`)
- `media_type` (derived: `image` | `video` | `other`, from a mime→media_type map)

**Critical correctness property**: Tier 1 detects corrupted files that have a valid
extension but invalid content (a truncated JPEG, a renamed MP3 with a `.mp4` extension,
a zero-byte file). The current extension-only scan cannot detect these. Moving mime
detection into the scan loop makes the emitted file set accurate by definition, not merely
probable.

### Tier 2 — Expensive (full file parse or sha256 + attribute cache)

Requires reading substantial file content or computing a full checksum. Cost scales with
file size. For a 4 GB video file, sha256 alone takes several seconds.

Tier 2 is sub-classified into three cost bands:

**Tier 2a — header parse, no sha256** (fast relative to Tier 2b/c):
- `resolution` (image: reads IHDR/SOF0 marker; video: reads moov atom for
  faststart-optimized MP4 — cost is proportional to header size, not file size)
- `duration` (video container header; same caveat: non-faststart MP4 has moov at end,
  making this effectively Tier 2b in that case)
- These shall be resolved in a dedicated pass without ever computing sha256.

**Tier 2b — full content decode** (medium-slow, scales with file size):
- `average_hash_v1` (perceptual hash — requires full image decode, then hash)
- Cost for a large image: tens to hundreds of milliseconds.

**Tier 2c — sha256-keyed bav attribute cache** (slow, scales with file size):
- All bav-specific cached attributes require sha256 as a lookup key.
- sha256 for a 4 GB file: several seconds even on SSD.
- This tier shall only be accessed when attributes from no other tier suffice.

Under the new design, `mime_type` and `media_type` are **removed from Tier 2** entirely.
The current `slow_btask` resolves mime_type, resolution, and duration in one pass because
mime_type was historically needed at that phase. It no longer is.

---

## Acceptance Criteria vs Sort Criteria

These are two orthogonal concepts that the current code conflates. Separating them is
fundamental to the new design.

**Acceptance criteria** — does this file belong in the result set at all?
Determined entirely during Phase 1 scan using Tier 1 mime detection. A file passes if
its detected `media_type` matches the requested types. Extension alone is never the
definitive gate; it is only a cheap pre-filter to avoid opening irrelevant files.
Corrupted files with valid extensions are rejected. Files with no recognized extension
but valid media magic bytes may be accepted (configurable).

**Sort criteria** — how should accepted files be ordered?
Applied after some or all files are accepted. Sort criteria are independent of
acceptance. The `found_order` sort type means "use emission order" — no sort pass runs
during or after the scan. Any other sort type triggers a sort pass (fast or slow) as
a separate step.

This separation means the scan phase is always the same regardless of what sort the
user has chosen. The sort type does not affect which files are found; it only affects
how they are displayed after they are found.

---

## Revised State Machine

```
IDLE → SCANNING → READY_QUICK → RESOLVING_SLOW → READY_SLOW
```

The FILTERING state is collapsed into the SCANNING→READY_QUICK transition (sort is
synchronous and fast enough to not warrant a visible state). Changes from current:

- **SCANNING** now covers the full Tier 0 + Tier 1 pass in a single btask. Files are
  emitted only after mime verification. Progress reports two counters: files accepted
  (`found`) and files examined (`scanned`).
- **READY_QUICK**: all emitted files have Tier 0 + Tier 1 attributes. If sort type is
  `found_order`, this state is immediately terminal — no sort pass. For fast sort types
  (name, date, size, path, kind, media_type, is_favorite, is_tagged, random, none), a
  synchronous sort pass runs at transition time. `kind` moves from slow to quick.
- **RESOLVING_SLOW**: only triggered if sort type requires Tier 2 attributes (resolution,
  width, height, aspect_ratio, duration, average_hash_v1). One btask per file. Uses
  Tier 2a (header parse) for resolution/duration; Tier 2b for average_hash_v1.
- **READY_SLOW**: Tier 2 resolved, final sort applied.

### Sort Tier Reclassification

**found_order** (default): emission order, no sort pass, READY_QUICK is terminal.

Fast (Tier 0 + 1, synchronous sort at READY_QUICK, no RESOLVING_SLOW):
- name, name_lowercase, path, path_lowercase, date, size, random, none
- **kind** (mime_type) — moves from slow to fast
- **media_type** — new, derived at scan time
- is_favorite, is_tagged (tag attributes remain as-is)

Slow (Tier 2a/2b, require RESOLVING_SLOW phase):
- resolution, width, height, aspect_ratio, duration (Tier 2a — header parse)
- average_hash_v1 (Tier 2b — full decode)

---

## Scan Progress Reporting

The current scan reports a single running count ("scanned 666 files"). The new scan
reports two independent counters throughout the scan loop:

- **scanned**: total filesystem entries examined (monotonically increasing, unbounded)
- **found**: files that passed all filters and were accepted (subset of scanned)

Progress message shape: `found {found}  scanned {scanned}` with no percentage, because
the total directory size is unknown until the walk completes. This is honest — it does
not imply indeterminate progress is a failure mode, it just means the scan is traversal-
order and the end is unknown.

The transition from indeterminate ("scanning") to determinate ("resolving") happens when
SCANNING ends and RESOLVING_SLOW begins. At that point the total count is known and
percentage progress becomes meaningful: `resolving {done} / {total}`.

---

## Mime Type Caching Efficiency Analysis

### On-the-fly vs cached, SSD

For N files on a fast SSD (random 4K latency ~0.1 ms):
- **On-the-fly magic bytes**: N × 0.1 ms = 100 ms per 1,000 files. Negligible.
- **xattr read** (if cached from prior scan): N × 0.01 ms = 10 ms per 1,000 files.
  Marginally faster. Not worth the implementation complexity on SSD alone.
- **sha256 cache lookup** (current approach): requires computing sha256 first.
  sha256 for a 100 MB file takes ~200 ms. For 1,000 such files: **200 seconds**.
  This is the source of the current slowness. It is not a caching problem; the cache
  key itself is expensive to compute.

Conclusion for SSD: **compute mime type on-the-fly every scan**. No caching needed.
The ~100 ms for 1,000 files is below perception threshold.

### On-the-fly vs cached, platter disk

For N files on a platter disk (random seek + read ~8–15 ms):
- **On-the-fly magic bytes**: N × 10 ms = 10 seconds per 1,000 files. Tolerable.
- **xattr read** (if cached): N × 0.1 ms = 100 ms per 1,000 files. 100× faster.
  For 10,000 files: 1 second vs 100 seconds. **Worth it on platter.**
- **sha256 cache lookup**: still requires sha256 first — even worse on platter due
  to sequential read cost for large files.

Conclusion for platter: xattr caching of mime type (and media_type) saves real time
on repeated opens of the same large directory. The xattr is written on first scan;
subsequent opens read it with a single metadata syscall (no content I/O).

### xattr Invalidation

An xattr cached mime type can become stale if the file content changes. The cache
entry shall be invalidated if the file's `(size, mtime)` pair has changed since the
xattr was written. This requires storing the (size, mtime) alongside the cached mime
type in the xattr value. No sha256 needed for invalidation.

Loss of xattrs (FAT filesystem, cross-filesystem copy, `xattr -c`) is handled by
falling back to on-the-fly detection transparently.

---

## New Components

### `bf_media_file_entry`

A lightweight, bes-level value object representing a single scanned media file. Contains
only Tier 0 + Tier 1 attributes. No sha256, no bav dependency.

Fields: `filename`, `size`, `mtime`, `extension`, `mime_type`, `media_type`

This is the type emitted by the scan phase and stored as the core identity of each file
in the media finder's result set. Tier 2 attributes are resolved separately and stored
externally (keyed by filename or as a decorator on this entry).

This type replaces `bav_file_entry` as the core entry type for the media pipeline.
`bav_file_entry` shall be retired; bav components that currently depend on it shall
migrate to `bf_media_file_entry` for Tier 0/1 attributes and use explicit Tier 2
resolvers for any attributes beyond that.

### `bf_media_scanner`

Wraps `bf_file_scanner` and adds inline Tier 1 detection. Single btask, single pass.

- Accepts root dirs, a set of requested media types (`image`, `video`), optional ignore
  filename.
- For each file: reads magic bytes via `bf_mime_type_detector` (with optional xattr
  cache), derives `media_type`. Extension is ignored for acceptance; mime type is
  authoritative.
- Emits `bf_media_file_entry` objects only for files where `media_type` matches the
  requested types. Corrupted or misextended files are silently excluded.
- Reports `(found: int, scanned: int)` counters in each progress batch.

### `bf_mime_xattr_cache`

Optional optimization layer over `bf_mime_type_detector`.

- On cache miss: calls `bf_mime_type_detector.detect_mime_type(filename)` and stores
  the result as an xattr `user.bf.mime_type` with `(size, mtime)` as a validity key.
- On cache hit: reads xattr, validates `(size, mtime)`, returns cached mime type.
- Falls back gracefully if xattrs are unavailable on the filesystem.
- Platform-aware: uses `xattr` module on macOS/Linux, skips on Windows.
- Can be disabled entirely at the `bf_media_scanner` constructor level.

---

## Requirements

### R1 — Component Location and Dependencies

- The component shall live in `bes/files/media_finder/`.
- The component shall have no dependency on Qt, rapp, rui, or bav.
- The component shall depend only on bes-internal modules plus the abstract preview
  provider interface defined below.
- All callbacks shall be plain Python callables, not Qt signals.

### R2 — Scan Phase

- The component shall accept one or more root directory paths and a set of requested
  media types (`image`, `video`).
- It shall delegate directory traversal to `bf_file_scanner` (via `bf_media_scanner`).
- It shall support an optional ignore filename (e.g. `.bes_ignore`).
- It shall apply built-in filename filters (`.part` suffix, `._` basename prefix,
  non-existent files) before opening any file.
- It shall perform Tier 1 mime detection inline for each candidate file and emit only
  files whose detected `media_type` matches the requested types. Corrupted files with
  invalid magic bytes shall be silently excluded.
- It shall emit `bf_media_file_entry` objects (not raw filenames) so callers receive
  Tier 0 + Tier 1 attributes together without a second pass.
- It shall report progress via `on_scan_progress(found: int, scanned: int)` where
  `found` is the accepted-so-far count and `scanned` is the total files examined.
  Progress is indeterminate (no percentage); callers shall not present a progress bar.
- It shall report scan completion via `on_scan_done(entries: list[bf_media_file_entry])`.
- It shall support cancellation at any point; no callbacks shall fire after cancellation.
- Starting a new scan while one is in progress shall cancel the previous scan first.
- The default sort type shall be `found_order`. In this mode files are visible
  immediately as the scan emits them with no sort pass. The user sees progressive
  results without any re-ordering during or after the scan.

### R3 — Metadata Resolution Phase (Tier 2 only)

- Triggered only when the active sort type requires Tier 2 attributes (resolution,
  width, height, aspect_ratio, duration, average_hash_v1). Not triggered for
  `found_order` or any fast sort type.
- `mime_type` and `media_type` are **not** resolved here; they are available from the
  scan phase (Tier 1).
- The component shall dispatch one btask per file to resolve whatever Tier 2 attributes
  are needed for the current sort type, not always all attributes.
- Resolution and duration shall be resolved via direct header parse (Tier 2a) — no
  sha256 computation. Image dimensions from IHDR/SOF0 marker; video duration from
  container header (moov atom). These shall never touch the sha256 attribute cache.
- `average_hash_v1` shall be resolved via full image decode (Tier 2b).
- sha256-keyed bav attributes (Tier 2c) shall only be resolved if explicitly required
  by a registered attribute resolver that cannot satisfy the request via 2a/2b.
- It shall report per-file completion via `on_resolve_progress(done: int, total: int)`.
  This phase is determinate: total is known before it starts.
- It shall report completion via `on_resolve_done()`.
- It shall debounce intermediate re-sort notifications (default 250 ms).
- Individual file errors shall be silently discarded.
- Cancellation is supported; in-flight tasks are cancelled on cancel or new scan.

### R4 — State Machine

- The component shall expose a discrete state: IDLE, SCANNING, READY_QUICK,
  RESOLVING, READY.
- State transitions shall be reported via an `on_state_changed(state)` callback.
- The component shall enforce valid transition ordering and raise an error for
  illegal transitions.

### R5 — Cancellation and Reset

- The component shall expose a `cancel()` method that cancels all in-progress scan
  and resolve tasks and transitions to IDLE.
- After `cancel()`, the component shall be ready to accept a new scan immediately.

### R6 — Abstract Preview Provider

- A `bf_preview_provider_i` abstract interface shall be defined in
  `bes/files/media_finder/` or `bes/files/preview/`.
- It shall expose:
  - `has_preview(filename, options) → bool`
  - `get_cached_preview(filename, options) → path | None`
  - `get_preview_async(filename, options, callback)` where callback receives
    `(filename, preview_path)` or an error indicator
  - `cancel_all()` — cancels all in-progress async requests
  - `cancel_for_file(filename)` — cancels a specific file's in-progress request
- The interface shall carry no dependency on specific image or video libraries.
- Concrete implementations (image thumbnail via PIL/cv2, video frame via ffmpeg,
  face detection via bav) shall live in rapp or bav and be injected at construction
  time.
- The preview cache (sha256-keyed, on-disk) shall be managed by a separate
  `bf_preview_cache` class in bes that the concrete implementations use, so the
  caching logic is testable independently of the generation logic.

### R7 — CLI Factory and Test Harness

- The component shall provide a CLI entry point (e.g. `bf_media_finder_cli`) that:
  - Accepts one or more root directories and a media type filter
  - Runs the scan phase and prints filenames as they arrive
  - Optionally runs the metadata resolution phase and prints results
  - Reports timing and counts
- This entry point shall serve as an integration test harness usable without Qt.
- There shall be no requirement for a running display server or GUI toolkit.

### R8 — Unit Tests

- Scan phase: test with a temp directory tree containing known files (including known-
  corrupted files with wrong magic bytes); verify only valid media files are emitted.
- `bf_media_file_entry` attributes: verify mime_type and media_type are correctly
  populated by scan, not left for the resolve phase.
- Progress counters: verify `scanned` grows monotonically and `found ≤ scanned` always.
- Scan cancellation: verify no callbacks fire after cancel is called.
- Concurrent scan replacement: verify that starting a second scan cancels the first.
- Mime detection: verify a file with `.jpg` extension but PNG magic bytes is identified
  as `image/png` and not `image/jpeg`.
- Corrupted file exclusion: verify a zero-byte `.mp4` or a text file renamed to `.jpg`
  is excluded from emitted results.
- Metadata resolution: verify mime_type is NOT re-resolved in Tier 2; verify only the
  attributes needed for the active sort type are fetched.
- Progress callbacks: verify they sum to total and done fires exactly once.
- State machine: verify all valid transitions; verify illegal transitions raise.
- Filter rules: verify `.part`, `._`-prefixed, and non-existent files are excluded.
- xattr cache: verify cache hit avoids file content I/O; verify invalidation on
  mtime/size change; verify graceful fallback when xattrs unavailable.
- Preview provider interface: test with a stub implementation that returns fixed
  paths; verify the caching layer is exercised separately from generation.

### R9 — Qt / rui Adaptor Layer

- A thin `rui_media_finder` adaptor class in rapp shall wrap `bf_media_finder` and
  translate its plain callbacks into pyqt signals matching the existing
  `rui_media_list` signal surface:
  - `scan_started`, `scan_progress(int)`, `scan_finished(int)`
  - `resolve_started(int)`, `resolve_progress(int, int)`, `resolve_finished()`
  - `state_changed(object)`
- The adaptor shall be the only Qt-dependent piece of the media finder stack.
- `rui_media_list` shall be refactored to delegate scan and resolve entirely to
  `rui_media_finder`, retaining only display logic (item creation, icon management,
  sort, scroll, selection).

---

## Future Requirements

These are listed to ensure the architecture is not hostile to them, even if they
are not implemented now.

### F1 — File System Monitoring

- The component shall be extensible to watch root directories for changes
  (new files, deleted files, renames) using OS-native APIs (FSEvents on macOS,
  inotify on Linux).
- New files shall be reported through the same `on_scan_batch` callback without
  requiring a full re-scan.
- Deleted files shall be reported via an `on_files_removed(filenames)` callback.
- Monitoring shall be optional and off by default; it shall be activatable after
  the initial scan completes.

### F2 — Tiered / Progressive Previews

- The current preview system generates one preview per file at a fixed quality.
  The future system shall support multiple quality tiers:
  - **Quick**: low-cost thumbnail (e.g. first raw video frame, no face detection,
    downsampled fast); produced immediately.
  - **Standard**: current-quality preview (resized, de-noised, basic selection).
  - **Enhanced**: face-detection-guided frame selection for video, slow but best result.
- The provider interface shall support a `quality` parameter so callers can request
  a specific tier.
- The cache shall be keyed by (sha256, quality) so tiers do not overwrite each other.
- A file shall display a quick preview immediately, then upgrade to a better preview
  when it becomes available, without the caller having to re-request.
- Enhanced previews shall be triggerable manually (user-requested) rather than
  running automatically for all files.

### F3 — Metadata Extensibility

- The metadata resolution phase shall be extensible: additional attributes (e.g.
  GPS coordinates, color profile, audio channel count) shall be addable by
  registering a resolver for a mime type without changing the core component.

### F4 — Result Persistence and Warm Start

- The component shall optionally persist the scanned file list so that on the next
  open of the same directory the initial file list is shown immediately from cache
  while a fresh scan runs in the background to detect changes.
- Stale entries (files no longer present) shall be pruned when the background scan
  completes.

### F5 — xattr Mime Cache as Default

- On platforms where xattrs are reliably available (macOS, Linux with ext4/btrfs/xfs),
  enable `bf_mime_xattr_cache` by default in `bf_media_scanner` so repeated opens of
  the same large directory on platter disks are fast.
- Provide a scanner option to disable it explicitly.
- Consider extending xattr caching to Tier 2 attributes (resolution, duration) to
  avoid sha256 computation on repeat scans, using the same (size, mtime) invalidation
  key. This would make Tier 2 resolution cheap on repeat opens without requiring the
  full sha256 attribute cache system.

---

## Implementation Plan — MVP CLI

Goal: a working `./r bin/best2.py media find /foo/bar` command that exercises the
scan phase end-to-end with callbacks, status output, and cancel support. Tier 2
resolution, xattr caching, preview, and Qt/rui adaptor are all deferred.

### CLI Design

Command path: `media find`

```
./r bin/best2.py media find <dir> [<dir> ...] [options]
```

Flag proposals (the user asked for a better name than `--match`):

| Flag | Values | Default | Notes |
|------|--------|---------|-------|
| `--media-type` | `image`, `video`, `all` | `all` | clearer than `--match`; `all` means image+video |
| `--sort` | `found_order`, `name`, `date`, `size`, `path`, `kind` | `found_order` | `kind` = by mime_type; string sorts are case-insensitive by default |
| `--case-sensitive` | flag | off | make string sorts (`name`, `path`, `kind`) case-sensitive |
| `--ignore-file` | basename string | `.bes_ignore` | per-directory ignore file; `""` to disable |
| `--verbose` / `-v` | flag | off | print one filename per result as scan progresses |
| `--count` | flag | off | print only final count, not filenames |

Progress output (stderr, overwrite same line):
```
  scanning:  found 142  scanned 1,847
```
On done (stderr):
```
  done: 142 files in 0.8s
```
Filenames to stdout (one per line, in chosen sort order), so output is pipeable.

On SIGINT: print `cancelled` to stderr, exit with code 1. No partial output to stdout.

### Files to Create

All new files live under `bes/files/media_finder/` unless noted.

```
bf_media_file_entry.py           — Tier 0+1 value object
bf_media_finder_state.py         — state enum
bf_media_sort_type.py            — sort type enum (MVP subset)
bf_media_scan_task.py            — btask worker function
bf_media_finder_callbacks.py     — plain callbacks struct
bf_media_finder_options.py       — core options (bcli_options subclass)
bf_media_finder.py               — core component
bf_media_find_cli_options.py     — CLI options (bcli_options subclass, adds UI fields)
bf_media_find_command_factory.py — bcli_command_factory_base subclass
bf_media_find_command_handler.py — bcli_command_handler subclass
__init__.py
```

One line added to `bes/cli/bes_application.py`: register
`bf_media_find_command_factory` in `parser_factories()`.

### Step-by-Step Implementation Order

#### Step 1 — `bf_media_file_entry`

Frozen dataclass. Fields: `filename` (str), `size` (int), `mtime` (float),
`extension` (str), `mime_type` (str), `media_type` (str: `'image'`|`'video'`|`'other'`).
`__str__` returns `filename`. Register with `check.register_class`.

No methods beyond field access. Tier 2 attributes (resolution, duration, etc.) are
resolved separately and stored outside this object.

#### Step 2 — `bf_media_finder_state`

Enum: `IDLE`, `SCANNING`, `READY_QUICK`, `RESOLVING_SLOW`, `READY_SLOW`.

MVP only exercises `IDLE → SCANNING → READY_QUICK`. The other states are defined now
so callbacks and the Qt adaptor can reference them without a future API change.

#### Step 3 — `bf_media_sort_type`

Enum covering only fast sort types for MVP (no RESOLVING_SLOW needed):
`FOUND_ORDER`, `NAME`, `PATH`, `DATE`, `SIZE`, `KIND`.

No `_CI` variants — case sensitivity is a separate flag on the scan call, not encoded
in the sort type. String-keyed sort types (`NAME`, `PATH`, `KIND`) lower the key before
comparison when `case_sensitive=False` (the default).

Slow sort types (`RESOLUTION`, `WIDTH`, `HEIGHT`, `ASPECT_RATIO`, `DURATION`,
`AVERAGE_HASH_V1`) are defined but raise `NotImplementedError` if selected until
Tier 2 is added.

A `is_slow` property on the enum distinguishes the two groups.

#### Step 4 — `bf_media_scan_task`

The btask worker. Classmethod `scan_task(context, args)` pattern matching
existing `scan_btask` / `slow_btask`.

`args` keys:
- `root_dirs`: list of str
- `media_types`: frozenset of `'image'`|`'video'`
- `ignore_filename`: str | None (e.g. `'.bes_ignore'`)

Logic:
1. Build `bf_file_ignore(ignore_filename)` if `ignore_filename` is set.
2. Walk with `bf_file_scanner`, applying `bf_file_ignore.should_ignore()` per dir.
3. Per file: apply filename filters (skip `.part` suffix, `._` prefix).
4. Read mime type via `bf_mime_type_detector.detect_mime_type(filename)`.
   Extension is ignored — mime is authoritative.
5. Derive `media_type` from mime type using `bf_mime_media` map.
6. If `media_type` not in requested `media_types`: skip.
7. Construct `bf_media_file_entry` and add to batch.
8. Every 50 accepted files (or when batch fills): emit `btask_status` with
   `{'entries': batch, 'found': found_so_far, 'scanned': scanned_so_far}`.
10. After emit: check `context.was_cancelled()`; if True, return immediately.

Returns `{'found': int, 'scanned': int}` on completion (used by `on_scan_done`).

#### Step 5 — `bf_media_finder_callbacks`

Simple dataclass (not frozen) of optional callables. All default to `None`.

```python
on_scan_progress(found: int, scanned: int) -> None
on_scan_done(entries: list[bf_media_file_entry]) -> None
on_state_changed(state: bf_media_finder_state) -> None
on_error(exc: Exception) -> None
```

Caller sets only the callbacks it cares about. `bf_media_finder` checks `is not None`
before calling each. Passed to `scan()`, not stored at construction time, so the same
finder instance is reusable with different callbacks.

#### Step 6 — `bf_media_finder_options`

`bcli_options` subclass (same infrastructure as `bf_file_resolver_options`) holding
all parameters that govern a scan. Not CLI-specific — used directly by
`bf_media_finder.scan()` and by any non-CLI caller.

Options desc:
```
   media_types  bf_media_cli_type  default=ALL
     sort_type  bf_media_sort_type default=FOUND_ORDER
   ignore_file  str                default=.bes_ignore
 case_sensitive bool               default=False
```

`bf_media_cli_type` is a small bcli type class (like `bf_cli_file_type`) that maps
`image` / `video` / `all` to a frozenset of media type strings.

Register with `check.register_class` so callers can do
`check.check_bf_media_finder_options(options, allow_none=True)`.

#### Step 7 — `bf_media_finder`

Constructor:
```python
def __init__(self, processor, num_scan_workers=2):
    check.check_btask_processor(processor)
    check.check_int(num_scan_workers)
```

`processor` is injected — the CLI creates its own; the Qt app injects the shared one.

Public API (MVP):
```python
def scan(self, root_dirs, options=None, callbacks=None): ...
def cancel(self): ...
@property
def state(self): ...
```

`options` is a `bf_media_finder_options` (`allow_none=True`, defaulting to a default
instance). `sort_type` defaults to `FOUND_ORDER`. Fast sort types sort the accumulated
entry list synchronously at transition to `READY_QUICK`. Slow sort types raise
`NotImplementedError` for now.

Internal flow:
1. If state is not IDLE: cancel in-flight scan first, wait for IDLE.
2. `_transition(SCANNING)` → fires `on_state_changed`.
3. Submit scan task to processor with category `'scan'`, priority `'normal'`,
   `num_scan_workers` tasks, passing `options` fields as task args.
4. On each status callback (from result collector thread): fire `on_scan_progress`,
   accumulate entries.
5. On task done: apply sort if not `FOUND_ORDER`, `_transition(READY_QUICK)`,
   fire `on_scan_done(all_entries)`.
6. On cancel: cancel task id, clear accumulated entries, `_transition(IDLE)`.

Thread safety: `_entries` accumulation and state transitions must be guarded by a
lock since status callbacks arrive on the result collector thread.

#### Step 8 — `bf_media_find_cli_options`

Follows the `bcli_options` / `bcli_options_desc` pattern from
`bf_file_resolver_cli_options`. Adds UI-only fields on top of the finder options
fields, and exposes a `finder_options` property.

Options desc (all finder fields plus CLI-only additions):
```
   media_types  bf_media_cli_type  default=ALL
     sort_type  bf_media_sort_type default=FOUND_ORDER
   ignore_file  str                default=.bes_ignore
 case_sensitive bool               default=False
       verbose  bool               default=False
         count  bool               default=False
         debug  bool               default=False
```

`finder_options` property:
```python
@property
def finder_options(self):
    return bf_media_finder_options(
        media_types=self.media_types,
        sort_type=self.sort_type,
        ignore_file=self.ignore_file,
        case_sensitive=self.case_sensitive,
    )
```

The handler calls `finder.scan(where, options=options.finder_options, callbacks=cbs)`.
CLI-only fields (`verbose`, `count`, `debug`) never leak into the core component.

#### Step 9 — `bf_media_find_command_factory` + `bf_media_find_command_handler`

**Factory** (`path()` returns `'media'`):
- Registers subcommand `find` with the flags above.
- `where` positional: `nargs='+'`, one or more directories.

**Handler** (`_command_find` method):
```python
def _command_find(self, where, options):
    import threading, signal, sys, time

    processor = btask_processor('media_find', num_processes=4)
    finder = bf_media_finder(processor, num_scan_workers=2)

    done_event = threading.Event()
    all_entries = []
    start = time.monotonic()

    def _progress(found, scanned):
        sys.stderr.write(f'\r  scanning:  found {found:,}  scanned {scanned:,}    ')
        sys.stderr.flush()

    def _done(entries):
        all_entries.extend(entries)
        done_event.set()

    def _error(exc):
        sys.stderr.write(f'\nerror: {exc}\n')
        done_event.set()

    cbs = bf_media_finder_callbacks(
        on_scan_progress=_progress,
        on_scan_done=_done,
        on_error=_error,
    )

    def _sigint(sig, frame):
        finder.cancel()

    signal.signal(signal.SIGINT, _sigint)

    finder.scan(where, options=options.finder_options, callbacks=cbs)
    done_event.wait()

    elapsed = time.monotonic() - start

    if finder.state == bf_media_finder_state.IDLE:  # cancelled
        sys.stderr.write('\ncancelled\n')
        return 1

    sys.stderr.write(f'\r  done: {len(all_entries):,} files in {elapsed:.1f}s\n')

    if not options.count:
        for entry in all_entries:
            print(entry.filename)
    else:
        print(len(all_entries))

    return 0
```

#### Step 10 — Register in `bes_application`

Add `bf_media_find_command_factory` to the `parser_factories()` list in
`bes/cli/bes_application.py`.

### What to Defer

The following are explicitly out of scope for the MVP. They slot in without API
changes:

| Deferred item | Where it fits |
|---------------|---------------|
| Tier 2 resolution (resolution, duration, average_hash) | Add `RESOLVING_SLOW` state and `--sort resolution` etc. |
| `bf_mime_xattr_cache` | Wrap `bf_mime_type_detector` call in `bf_media_scan_task` |
| Qt/rui adaptor (`rui_media_finder`) | Wraps `bf_media_finder`, translates callbacks to signals |
| `rui_media_list` refactor | Delegates to `rui_media_finder`, keeps display logic |
| Abstract preview provider | Separate work item, not needed for CLI |
| File system monitoring | Future (F1) |
| Result persistence / warm start | Future (F4) |

### Integration Test Checklist

Once Step 10 is done, verify manually before writing unit tests:

```bash
# basic image scan
./r bin/best2.py media find ~/Pictures --media-type image

# video only, verbose (prints as found)
./r bin/best2.py media find ~/Movies --media-type video --verbose

# mixed, count only
./r bin/best2.py media find /some/mixed/dir --count

# ignore .bes_ignore files
./r bin/best2.py media find /dir/with/ignores

# disable ignore file
./r bin/best2.py media find /dir --ignore-file ""

# sort by name (case-insensitive by default)
./r bin/best2.py media find ~/Pictures --sort name

# sort by name, case-sensitive
./r bin/best2.py media find ~/Pictures --sort name --case-sensitive

# Ctrl+C during large scan — verify "cancelled" on stderr, exit 1, no stdout output
./r bin/best2.py media find /large/dir   # then ^C

# corrupted file detection: create a .jpg with PNG magic bytes in a test dir
# verify it appears in output as image/png, not excluded as corrupt jpeg
```

### Unit Test Targets (after integration verified)

- `bf_media_file_entry`: fields, frozen, `check.check_bf_media_file_entry()`
- `bf_media_scan_task`: fixture dir with valid, corrupt, and misextended files;
  assert only valid media emitted; assert `scanned >= found` always
- `bf_media_finder.scan`: scan fires `on_scan_done` exactly once; progress counter
  is non-decreasing; cancel mid-scan fires no further callbacks; state returns to IDLE
  after cancel; second scan after cancel works cleanly
- Sort: `NAME` and `DATE` produce correctly ordered results on a known fixture dir
- Mime correctness: `.jpg` file with PNG header classified as `image/png` not excluded
