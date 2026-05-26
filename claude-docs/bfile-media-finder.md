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
- `duration` (video container header — may be absent in some formats)

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
IDLE → SCANNING → READY_QUICK → RESOLVING → READY
```

The FILTERING state is collapsed into the SCANNING→READY_QUICK transition (sort is
synchronous and fast enough to not warrant a visible state).

RESOLVING_SLOW and READY_SLOW are renamed RESOLVING and READY to drop the
"slow" qualifier — the async resolve phase hides latency from the UI regardless of
how expensive the computation is.

- **SCANNING**: full Tier 0 + Tier 1 pass in a single btask. Files emitted only after
  mime verification. Progress reports two counters: `found` (accepted) and `scanned`
  (examined).
- **READY_QUICK**: all files have Tier 0 + Tier 1 attributes. If sort type is a builtin,
  this state is terminal (or a synchronous sort pass runs at transition time).
- **RESOLVING**: only triggered if sort type is an extended sort key.
- **READY**: extended attrs resolved, final sort applied.

**IDLE transition always discards all accumulated entries regardless of which state
is active.** `resolved_attrs` on individual entries does not need explicit clearing
because the entries themselves are dropped.

### Sort Type Classification

Sort types fall into two categories:

**Intrinsic** — sort key is derived from data the finder already holds (Tier 0 + 1).
Always available without a resolver. READY_QUICK is terminal (or a synchronous sort
pass runs at transition time). Values are `bf_media_sort_type` enum members:
`FOUND_ORDER`, `NAME`, `PATH`, `DATE`, `SIZE`, `KIND`.

**Extended** — sort key requires an injected attr resolver (Tier 2). Sort type is a
plain string matching the `attr_name` the resolver handles (e.g. `'resolution'`,
`'duration'`). These strings never appear in `bes` source — they are owned entirely
by the resolver implementation in `rui` (or wherever the concrete resolver lives).
Triggers RESOLVING → READY after READY_QUICK.

The distinction is: `isinstance(sort_type, bf_media_sort_type)` → intrinsic;
`isinstance(sort_type, str)` → extended.

---

## Scan Progress Reporting

Two independent counters throughout the scan loop:

- **scanned**: total filesystem entries examined (monotonically increasing)
- **found**: files accepted (subset of scanned)

Progress message: `found {found}  scanned {scanned}` with no percentage.

---

## Attr Resolver Interface

`bes` defines the interface and registry. No PIL, av, opencv, or bav imports anywhere
in `bes`. Concrete implementations live in `rui` (or `bav`) and are injected at
startup.

### `BF_ATTR_NOT_AVAILABLE` sentinel

A module-level singleton distinct from `None`. Used when a resolver attempted
computation but the file genuinely has no data for the requested attribute (e.g. a
video container format that does not store duration in its header).

```
return value                  — successfully computed
return BF_ATTR_NOT_AVAILABLE  — tried; file has no data for this attr
return None                   — this resolver does not handle this attr_name at all
```

For sorting, both `None` (missing key or unsupported) and `BF_ATTR_NOT_AVAILABLE`
(data absent from file) sort to the end. They carry different display semantics:
"—" (data absent) vs blank (attr not applicable to this file/resolver).

### `bf_media_attr_resolver_base`

Abstract base class in `bes`. No external dependencies.

```python
class bf_media_attr_resolver_base:
    name: ClassVar[str]   # unique string, e.g. 'pil_av'

    @classmethod
    def resolve(cls, filename: str, mime_type: str, attr_name: str) -> Any:
        # Returns: a value, BF_ATTR_NOT_AVAILABLE, or None
        raise NotImplementedError

    @classmethod
    def attr_sort_key(cls, value) -> tuple:
        'Return a sort key that places real values before None/NOT_AVAILABLE.'
        if value is None or isinstance(value, _bf_attr_not_available_type):
            return (1, None)
        return (0, value)
```

`attr_sort_key` is a classmethod on the base so it is available without a concrete
resolver instance. The finder builds the full sort key as:

```python
import os.path as path

key = lambda e: (
    resolver.attr_sort_key(e.resolved_attrs.get(options.sort_type)),
    path.basename(e.filename).lower(),
    path.dirname(e.filename).lower(),
)
entries.sort(key=key)
```

This avoids type-comparison errors (e.g. comparing `(1920, 1080)` with
`BF_ATTR_NOT_AVAILABLE`) and consistently places non-values at the end. The
`(basename, dirname)` tail is a universal stable tiebreaker applied by the finder;
domain-specific secondaries are encoded by the resolver in the primary value itself
(see Sort Criteria section).

`attr_name` is the exact sort key string. The resolver computes only what is asked
for — no wasted work.

### `bf_media_attr_resolver_registry`

Plain name → class dict in `bes`. Resolvers register themselves at import time.

```python
bf_media_attr_resolver_registry.register(MyResolver)   # keyed by MyResolver.name
bf_media_attr_resolver_registry.get('pil_av')          # → class; KeyError if unknown
bf_media_attr_resolver_registry.names()                # → list[str]
```

### Concrete resolver — lives in `rui`

```python
class rui_media_attr_resolver(bf_media_attr_resolver_base):
    name = 'pil_av'

    @classmethod
    def resolve(cls, filename, mime_type, attr_name):
        if attr_name == 'resolution':
            if mime_type and mime_type.startswith('image/'):
                from PIL import Image
                with Image.open(filename) as img:
                    return img.size          # (w, h) — header-only read
            elif mime_type and mime_type.startswith('video/'):
                import av
                with av.open(filename) as f:
                    for s in f.streams.video:
                        return (s.codec_context.width, s.codec_context.height)
            return None
        elif attr_name == 'duration':
            if mime_type and mime_type.startswith('video/'):
                import av
                with av.open(filename) as f:
                    for s in f.streams.video:
                        if s.duration and s.time_base:
                            return float(s.duration * s.time_base)
                return BF_ATTR_NOT_AVAILABLE  # video but no duration metadata
            return None
        return None

bf_media_attr_resolver_registry.register(rui_media_attr_resolver)
```

### Subprocess pickle behaviour

The btask resolve worker runs in a subprocess (spawn start method on macOS). The
resolver class is passed as part of the task args dict, which is serialised via
pickle. Pickle stores a class by `module + qualname` reference and reimports it in
the subprocess — so passing the class object works transparently provided the module
is on `PYTHONPATH` in the worker process (which it will be via inherited env).

---

## Sort Criteria

Every sort (intrinsic or extended) produces a comparison tuple of the form:

```
( primary_key, basename_lower, dirname_lower )
```

`(basename_lower, dirname_lower)` is the **universal filename tiebreaker** appended
by the finder. It is always present and ensures a stable, deterministic order when
the primary key is equal across multiple files (e.g. many videos at 1920×1080).

### Intrinsic sort key table

| Sort type | Primary key |
|---|---|
| `FOUND_ORDER` | no sort applied — emission order preserved |
| `NAME` | `(basename_lower,)` — dirname is the tiebreaker |
| `PATH` | `(filename_lower,)` — already fully qualified, dirname redundant but harmless |
| `DATE` | `mtime` (float) |
| `SIZE` | `size` (int bytes) |
| `KIND` | `mime_type` (string) |

### Extended sort key encoding

For extended sorts the resolver returns the primary value. `attr_sort_key(value)`
wraps it in `(0, value)` for real values or `(1, None)` for `BF_ATTR_NOT_AVAILABLE`
/ `None`, so non-values always sort **to the end**.

The old code placed not-yet-resolved entries at the **beginning** (using zero/empty
sentinel values such as `bav_size(0, 0)` or `0`). The new design puts them at the
**end** via `BF_ATTR_NOT_AVAILABLE`. This is intentional and unambiguous.

**Domain-specific secondaries are encoded inside the resolver's return value**, not
added by the finder. When a sort type has a natural domain tiebreaker, the resolver
returns a tuple whose elements encode that ordering:

| attr_name | resolve() returns | Sort semantics |
|---|---|---|
| `resolution` | `(w, h)` | wider first; taller as secondary for same width |
| `width` | `(w, h)` | wider first; height as secondary |
| `height` | `(h, w)` | taller first; width as secondary |
| `duration` | `float` seconds | shorter first |
| `aspect_ratio` | `float` | narrower first |
| `average_hash_v1` | `int` | by hash value |

The finder sees an opaque value and applies `attr_sort_key` uniformly. It has no
knowledge of what `resolution` or `width` means.

**Full example** — `width` sort on a `1920×1080` file `b.mp4` in `/movies`:

```
( (0, (1920, 1080)), 'b.mp4', '/movies' )
```

**Full example** — same sort on a file with no readable video stream:

```
( (1, None), 'broken.mp4', '/movies' )
```

The broken file sorts after all files with real values, then by filename within the
not-available group.

---

## Resolve Task Result Shape

`bf_media_resolve_task` returns a plain dict:

```python
{'filename': str, 'attr_name': str, 'value': Any}
```

`value` may be a computed result, `BF_ATTR_NOT_AVAILABLE`, or `None`.

The finder builds a lookup table `{e.filename: e for e in self._entries}` before
dispatching resolve tasks. In the done callback it writes:

```python
entry = filename_index[result['filename']]
entry.resolved_attrs[result['attr_name']] = result['value']
```

---

## Cancel During Resolve

The finder maintains `self._resolve_task_ids: set` during RESOLVING. Each dispatched
task ID is added to the set and removed when its done callback fires.

`cancel()` iterates the set and spawns a daemon thread per cancellation, using the
same pattern already in place for scan cancel (avoids re-entrant deadlock when called
from a status or done callback that holds the processor lock).

On transition to IDLE from any state, `self._entries = []`. All accumulated entries
and their `resolved_attrs` are discarded.

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
`extension`, `mime_type`, `media_type`, `resolved_attrs` (dict, default empty via
`field(default_factory=dict)`). `relative_filename` property computed from the two
path fields. `__str__` returns `filename`. Registered with `check`.

The dataclass is frozen (field references immutable) but `resolved_attrs` is a plain
`dict` whose contents can be mutated. The resolve phase writes into it in place. The
existing `test_frozen` test continues to pass; a separate test covers that
`resolved_attrs` contents are mutable.

### `bf_media_sort_type`

Enum of **intrinsic sort types only**: `FOUND_ORDER`, `NAME`, `PATH`, `DATE`, `SIZE`,
`KIND`. Extended sort types (resolution, duration, etc.) are not enum members — they
are plain strings owned by the resolver implementation and never referenced in `bes`
source. The `is_slow` property and all slow-type enum values are removed.

### `BF_ATTR_NOT_AVAILABLE`

Module-level singleton in `bes/files/media_finder/bf_media_attr_not_available.py`.
Returned by resolvers when computation was attempted but the file has no data.

### `bf_media_attr_resolver_base`

Abstract base in `bes/files/media_finder/bf_media_attr_resolver_base.py`. Provides
`attr_sort_key(value)` classmethod for consistent sort ordering.

### `bf_media_attr_resolver_registry`

Name → class registry in `bes/files/media_finder/bf_media_attr_resolver_registry.py`.

### `bf_media_finder_state`

`IDLE`, `SCANNING`, `READY_QUICK`, `RESOLVING`, `READY`.

### `bf_media_finder_options`

`bcli_options` subclass. Fields:

| Field | Type | Default | Notes |
|---|---|---|---|
| `media_types` | frozenset | `{'image','video'}` | |
| `sort_type` | `bf_media_sort_type \| str` | `FOUND_ORDER` | string → extended sort |
| `sort_reversed` | bool | `False` | reverse the final sort order; applies to all sort types including `found_order` |
| `ignore_file` | `str \| None` | `None` | |
| `case_sensitive` | bool | `False` | |
| `attr_resolver` | `type[bf_media_attr_resolver_base] \| None` | `None` | required for extended sorts |
| `num_scan_workers` | int | 2 | populates `btask_config(limit=...)` for scan task |
| `scan_chunk_size` | int | 50 | files per `report_status` call in the scan worker |
| `num_resolve_workers` | int | 2 | populates `btask_config(limit=...)` for resolve tasks |
| `resolve_chunk_size` | int | 10 | files per resolve btask |

`attr_resolver` holds the **class itself** (not a name string) so it passes through
pickle to btask worker processes without a registry lookup in the subprocess.
`None` means extended sorts route to `on_error`.

`num_scan_workers` moves here from the `bf_media_finder` constructor (breaking change
to existing constructor API).

`scan_chunk_size` is passed to the scan worker via task args and replaces the
hardcoded `_BATCH_SIZE = 50` constant in `bf_media_scan_task`.

`resolve_chunk_size` controls how many files are packed into a single resolve btask.
The finder groups the full entry list into chunks of this size before dispatching,
so for 1,000 entries with `resolve_chunk_size=10` the processor receives 100 tasks
rather than 1,000. Each resolve task returns a list of result dicts.

### `bf_media_finder_callbacks`

Dataclass of optional callables:
- `on_scan_progress(found, scanned)`
- `on_scan_done(entries)`
- `on_resolve_progress(done, total)`
- `on_resolve_done()`
- `on_cancel()`
- `on_state_changed(state)`
- `on_error(exc)`

### `bf_media_finder`

Owns `btask_main_thread_runner_py` and `btask_result_collector_py`. Processor is
injected (CLI creates its own; Qt app injects shared one).

`scan(root_dirs, options=None, callbacks=None)` — starts the scan.
`cancel()` — cancels scan task and all live resolve task IDs; each cancellation is
deferred to a daemon thread to avoid re-entrant deadlock.
`run()` — blocks until scan (and resolve, if triggered) completes or is cancelled.

If `sort_type` is a string and `attr_resolver` is `None`, routes `ValueError` through
`on_error` without starting the resolve phase.

Maintains `self._resolve_task_ids: set` during RESOLVING; cleared on IDLE transition.
Builds `self._filename_index: dict[str, bf_media_file_entry]` before dispatching
resolve tasks for O(1) lookup in done callbacks.

### `bf_media_scan_task`

btask worker. Args: `root_dirs`, `media_types`, `ignore_filename`, `chunk_size`
(from `options.scan_chunk_size`). Walks dirs via `bf_file_scanner`, applies `.part`
/ `._` filename filters, detects mime via `bf_mime_type_detector` (extension
ignored), streams `bf_media_scan_status` batches of `chunk_size` accepted files.
Uses `raise_cancelled_if_needed` for proper CANCELLED result state.

`chunk_size` replaces the hardcoded `_BATCH_SIZE = 50` constant.

### `bf_media_resolve_task`

btask worker. Args: `entries` (list of `{'filename', 'mime_type'}` dicts, up to
`resolve_chunk_size` items), `attr_name`, `resolver` (class).

For each entry calls `resolver.resolve(filename, mime_type, attr_name)`. Returns a
list of result dicts: `[{'filename': ..., 'attr_name': ..., 'value': ...}, ...]`.
Per-file exceptions are caught silently; that file's result dict is omitted from the
list (the finder leaves the entry's `resolved_attrs` key absent).

The finder groups `self._entries` into chunks of `resolve_chunk_size` before
dispatching. For 1,000 entries with the default chunk size of 10, the processor
receives 100 tasks rather than 1,000.

---

## Requirements

### R1 — Component Location and Dependencies

- Lives in `bes/files/media_finder/`.
- No dependency on Qt, rapp, rui, bav, PIL, av, or opencv.
- All callbacks are plain Python callables, not Qt signals.
- Resolver implementations live outside `bes` and are injected via registry +
  `bf_media_finder_options.attr_resolver`.

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
- `num_scan_workers` from options populates `btask_config(limit=num_scan_workers)`.
- `scan_chunk_size` from options is passed to the worker and controls batch size for
  `report_status` calls.

### R3 — Metadata Resolution Phase (Tier 2)

- Triggered when `sort_type` is a string (extended sort).
- If `attr_resolver` is `None`, routes `ValueError` through `on_error` immediately.
- Dispatches one btask per file calling `resolver.resolve(filename, mime_type, attr_name)`.
- Resolver returns a value, `BF_ATTR_NOT_AVAILABLE`, or `None`; stored in
  `entry.resolved_attrs[attr_name]`.
- Sort uses `resolver.attr_sort_key(value)` to place non-values at the end without
  type-comparison errors.
- Debounces intermediate re-sort (default 250 ms); final sort when all resolved.
- Reports `on_resolve_progress(done, total)` and `on_resolve_done()`.
- Supports cancellation; all live resolve task IDs cancelled on new scan or explicit
  cancel; IDLE transition discards all entries.
- Per-file errors swallowed silently; that file's result is omitted from the chunk return.
- `num_resolve_workers` from options populates `btask_config(limit=num_resolve_workers)`.
- `resolve_chunk_size` from options controls files per resolve btask; entries are
  grouped into chunks before dispatch.

### R4 — State Machine

- Exposes discrete state: `IDLE`, `SCANNING`, `READY_QUICK`, `RESOLVING`, `READY`.
- Reports transitions via `on_state_changed(state)`.

### R5 — Cancellation and Reset

- `cancel()` cancels all in-progress tasks (scan and resolve) and transitions to IDLE.
- IDLE transition always discards all accumulated entries.
- Component is ready for a new scan immediately after cancel.

### R6 — CLI

- `best2.py media find <dir> [options]`
- Flags: `--media-type`, `--sort`, `--sort-reversed`, `--attr-resolver`,
  `--ignore-file`, `--case-sensitive`, `--verbose`/`-v`, `--count`
- `--sort` accepts any string. Builtin enum values handled directly; any other string
  is an extended sort key requiring `--attr-resolver NAME`.
- `--attr-resolver NAME` looks up the registry and stores the class in finder options.
- Progress to stderr; filenames to stdout (pipeable).
- SIGINT → cancel → exit 1.

### R7 — Unit Tests

#### `test_bf_attr_not_available.py` — new file

1. `test_is_not_none` — sentinel is not `None`
2. `test_is_singleton` — two references yield the same object (`is`)
3. `test_is_falsy` — `bool(BF_ATTR_NOT_AVAILABLE) == False`
4. `test_not_equal_to_zero` — `BF_ATTR_NOT_AVAILABLE != 0`
5. `test_not_equal_to_false` — `BF_ATTR_NOT_AVAILABLE != False`
6. `test_isinstance` — `isinstance(BF_ATTR_NOT_AVAILABLE, _bf_attr_not_available_type)`
7. `test_repr_nonempty` — `repr(...)` returns a non-empty string

#### `test_bf_media_attr_resolver_base.py` — new file (`attr_sort_key`)

8. `test_int_value` — `attr_sort_key(42)` → `(0, 42)`
9. `test_float_value` — `attr_sort_key(1.5)` → `(0, 1.5)`
10. `test_tuple_value` — `attr_sort_key((1920, 1080))` → `(0, (1920, 1080))`
11. `test_none_key` — `attr_sort_key(None)` → `(1, None)`
12. `test_not_available_key` — `attr_sort_key(BF_ATTR_NOT_AVAILABLE)` → `(1, None)`
13. `test_none_and_not_available_equal_key` — both produce identical tuples
14. `test_real_before_none` — `attr_sort_key(42) < attr_sort_key(None)`
15. `test_real_before_not_available` — `attr_sort_key(42) < attr_sort_key(BF_ATTR_NOT_AVAILABLE)`
16. `test_smaller_real_before_larger` — `attr_sort_key(1.0) < attr_sort_key(2.0)`
17. `test_tuple_ordering` — `attr_sort_key((640, 480)) < attr_sort_key((1920, 1080))`
18. `test_sort_list_mixed` — list of real values, `None`, `BF_ATTR_NOT_AVAILABLE` sorts with real values first, non-values at end, no `TypeError`

#### `test_bf_media_attr_resolver_registry.py` — new file

19. `test_register_and_get` — registered class retrieved by name
20. `test_get_unknown_raises` — `KeyError` for unregistered name
21. `test_names_contains_registered` — registered name appears in `names()`
22. `test_register_two_resolvers` — two different names both independently retrievable
23. `test_register_overwrites_same_name` — second registration with same name replaces first
24. `test_names_returns_list` — `names()` returns a `list`

#### `test_bf_media_sort_type.py` — update

**Remove:** `test_fast_types_not_slow` (`is_slow` gone), `test_slow_types_are_slow`
(slow enum values gone).

25. `test_all_intrinsic_values` — exactly six members: `FOUND_ORDER`, `NAME`, `PATH`, `DATE`, `SIZE`, `KIND`
26. `test_intrinsic_isinstance` — each enum value satisfies `isinstance(v, bf_media_sort_type)`
27. `test_string_not_isinstance` — `isinstance('resolution', bf_media_sort_type)` is `False`
28. `test_extended_string_not_parseable` — `bf_media_sort_type('resolution')` raises

#### `test_bf_media_file_entry.py` — update

**Update:** `test_fields` to include `resolved_attrs` defaulting to `{}`.
`test_frozen` updated: field assignment raises, but dict mutation does not.

29. `test_resolved_attrs_default_empty` — `entry.resolved_attrs == {}`
30. `test_resolved_attrs_mutable` — `entry.resolved_attrs['x'] = 1` succeeds; readable back
31. `test_resolved_attrs_field_frozen` — `entry.resolved_attrs = {}` raises `FrozenInstanceError`

#### `test_bf_media_finder_options.py` — update

**Update:** `test_defaults` to cover all new fields.

32. `test_sort_reversed_default` — `sort_reversed` defaults to `False`
33. `test_sort_reversed_true` — `sort_reversed=True` accepted

34. `test_scan_chunk_size_custom` — `scan_chunk_size=5` accepted
35. `test_resolve_chunk_size_custom` — `resolve_chunk_size=3` accepted
36. `test_num_scan_workers_custom` — `num_scan_workers=4` accepted
37. `test_num_resolve_workers_custom` — `num_resolve_workers=8` accepted
38. `test_attr_resolver_class` — `attr_resolver=SomeFakeResolverClass` accepted
39. `test_sort_type_extended_string` — `sort_type='resolution'` accepted without error

#### `test_bf_media_finder.py` — sort_reversed (new, in sort block)

40. `test_sort_name_reversed` — `sort_type='name', sort_reversed=True` produces reverse-alphabetical order
41. `test_sort_size_reversed` — `sort_type='size', sort_reversed=True` produces largest-first order
42. `test_sort_found_order_reversed` — `sort_type='found_order', sort_reversed=True` reverses emission order

#### `test_bf_media_finder.py` — update

**Update:** `test_sort_slow_raises` → `test_extended_sort_no_resolver_fires_on_error`
— extended sort with `attr_resolver=None` calls `on_error`; RESOLVING state never entered.

**State machine (resolve path):**

38. `test_resolve_state_transitions` — extended sort: `on_state_changed` sequence is SCANNING → READY_QUICK → RESOLVING → READY
39. `test_resolve_not_triggered_for_intrinsic` — intrinsic sort: RESOLVING and READY never appear in transition log
40. `test_final_state_ready_after_resolve` — `finder.state == READY` after extended sort completes

**Callbacks — ordering and counts:**

41. `test_on_scan_done_fires_before_resolving` — state at `on_scan_done` time is READY_QUICK, not RESOLVING
42. `test_on_resolve_progress_fires` — `on_resolve_progress` called at least once
43. `test_on_resolve_progress_done_monotonic` — `done` arg never decreases across calls
44. `test_on_resolve_progress_total_constant` — `total` arg is the same value on every call
45. `test_on_resolve_progress_total_equals_entry_count` — `total` matches entry count from `on_scan_done`
46. `test_on_resolve_progress_final_done_equals_total` — last call has `done == total`
47. `test_on_resolve_done_fires_once` — `on_resolve_done` called exactly once
48. `test_on_resolve_done_after_scan_done` — `on_scan_done` observed before `on_resolve_done`

**Resolved attrs population:**

49. `test_resolved_attrs_empty_at_scan_done` — all entries have `resolved_attrs == {}` at `on_scan_done` time
50. `test_resolved_attrs_populated_after_resolve` — after `run()` all entries have `resolved_attrs[attr_name]` set
51. `test_resolved_attrs_not_available_stored` — resolver returning `BF_ATTR_NOT_AVAILABLE` → stored in `resolved_attrs`
52. `test_resolved_attrs_none_stored` — resolver returning `None` → `None` stored in `resolved_attrs`

**Sort correctness:**

53. `test_sort_extended_real_values_ordered` — entries with real attr values appear in correct sorted order
54. `test_sort_extended_not_available_at_end` — `BF_ATTR_NOT_AVAILABLE` entries appear after all real-value entries
55. `test_sort_extended_none_at_end` — `None` entries appear after all real-value entries
56. `test_sort_extended_not_available_and_none_together` — `BF_ATTR_NOT_AVAILABLE` and `None` sort to the same end group without `TypeError`
57. `test_sort_extended_tuple_primary_domain_secondary` — resolver returning `(w, h)` tuple sorts correctly: wider before narrower, taller before shorter for same width
58. `test_sort_extended_filename_tiebreaker` — two entries with identical primary value sort by basename then dirname

**Chunk dispatch:**

59. `test_scan_chunk_size_controls_progress_frequency` — `scan_chunk_size=2`, 6 found files → at least 3 `on_scan_progress` calls before done
60. `test_resolve_single_chunk` — `resolve_chunk_size=100`, 5 entries → `on_resolve_progress` fires once with `done=5, total=5`
61. `test_resolve_multiple_chunks` — `resolve_chunk_size=2`, 5 entries → fires 3 times with `done` sequence 2, 4, 5
62. `test_resolve_chunk_size_one` — `resolve_chunk_size=1` → `on_resolve_progress` fires once per entry

**Cancel during resolve:**

63. `test_cancel_mid_resolve_transitions_to_idle` — cancel during RESOLVING → state becomes IDLE
64. `test_cancel_mid_resolve_on_cancel_fires` — `on_cancel` fires
65. `test_cancel_mid_resolve_no_progress_after` — `on_resolve_progress` does not fire after cancel
66. `test_cancel_mid_resolve_no_done_after` — `on_resolve_done` does not fire after cancel
67. `test_second_scan_after_mid_resolve_cancel` — scan after mid-resolve cancel completes cleanly to READY_QUICK

**Cross-phase interactions:**

68. `test_cancel_mid_scan_no_resolve_triggered` — cancel during SCANNING → RESOLVING never entered; `on_resolve_progress` never fires
69. `test_new_scan_during_resolve_cancels_resolve` — calling `scan()` while RESOLVING cancels in-flight resolve tasks; new scan reaches READY_QUICK
70. `test_resolver_exception_per_file_silently_skipped` — resolver raises for one file → that entry has no key in `resolved_attrs`; remaining entries resolved normally; `on_resolve_done` still fires

---

## Future Work

### F1 — File System Monitoring

Watch root directories for changes using OS-native APIs (FSEvents/inotify).
New files via same `on_scan_batch` callback. Deleted files via `on_files_removed`.
Off by default, activatable after initial scan.

### F2 — Metadata Extensibility

Additional attributes (GPS, color profile, audio channels) addable by registering
a new resolver class without changing the core component.

### F3 — Result Persistence and Warm Start

Optionally persist the scanned file list so the initial display is instant on
re-open while a background scan detects changes.

### F4 — xattr Mime Cache as Default

Enable `bf_mime_xattr_cache` by default on macOS/Linux for platter-disk performance.
Consider extending to Tier 2 attributes (resolution, duration) using same
(size, mtime) invalidation key.
