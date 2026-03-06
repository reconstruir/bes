# New btask Step Progress Plan

## Background

The existing `context.report_progress(minimum, maximum, value, message)` interface works for single-level
progress (a flat progress bar). It has a bug where the 1% drop filter in `_should_drop_progress` uses
a modulo check that fails for non-uniform values like ffmpeg millisecond timestamps — only exact multiples
of `one_percent` pass, which frame-boundary timestamps rarely hit.

The goal is a two-level progress system:
- **Step level**: "file 3 of 10: video.mp4" — which step we are on
- **Sub-step level**: "47% through transcoding video.mp4" — progress within a step

The new interface is `report_step_progress`. The old `report_progress` is left intact for backward
compatibility through all phases and retired only in the final phase after everything is tested.

---

## Current Usage Inventory

### Step + sub-progress (motivating case for new feature)
- `fdui_transcode_tasks.py` — per-file ffmpeg progress (outer loop = files, inner = ffmpeg %)
- `rui_video_trim_tasks.py` — single operation with ms-based sub-progress

### Step-only (N of M, no sub-progress)
- `fdui_redgifs.py:170` — iterating files
- `fdui_redgifs.py:212` — iterating files
- `fdui_similar_images_tasks.py:39` — comparing images
- `fdui_file_tasks.py:71` — staging files
- `fdui_file_tasks.py:90` — filing files
- `fdui_face_detect_tasks.py:79` — face detection per file
- `fdui_preview_tasks.py:54` — previews per file
- `redgifs_creator_window.py:205` — generic iteration

### Indeterminate (status text only, no meaningful range)
- `fdui_file_tasks.py:30,42,48,50` — trash operations

---

## Phase 1 — New btask interface in `bes` (backward compat)

Add alongside existing `report_progress`, do not modify it.

**New types:**
- `btask_step_progress` dataclass: `step` (int), `total_steps` (int), `step_title` (str),
  `step_percent` (int 0-100 or None for indeterminate)
- `btask_status_step_progress` wrapping it, parallel to existing `btask_status_progress`

**New context method:**
- `btask_function_context.report_step_progress(step, total_steps, step_title, step_percent=None)`

**Auto-throttling in `btask_function_context` (worker process side):**

The throttle lives in `report_step_progress` itself, inside `btask_function_context`, which runs
in the worker subprocess. The dedup check happens before `status_queue.put()`, so IPC never occurs
for duplicate calls. The manager process/thread never sees them. This is different from the old
`_should_drop_progress` which ran in the collector thread of the main process — too late, the IPC
cost had already been paid.

Dedup key: `(step, total_steps, step_percent)`. `total_steps` is included so the
indeterminate→determinate transition (`None→N`) is not accidentally dropped.

Drop rule: if key equals `_last_step_report`, increment `_step_drop_count` and return (no IPC).
Otherwise pass through, update `_last_step_report`, reset `_step_drop_count = 0`.

Warning log: when `_step_drop_count` reaches a threshold (e.g. 100), log once:
`"report_step_progress: auto-throttled {n} identical calls for step {step} — caller is reporting
too frequently, consider reducing call frequency"`. Reset counter after warning.

**Worker computes percent (simplification over old interface):**

Old interface required `report_progress(minimum, maximum, value, message)` — the worker carried
three numbers and the receiver inferred percent. IPC payload was larger and dedup key was awkward.
New interface: the worker has all context needed (it knows `duration_ms`, `total_files`, etc.) so
it computes a single 0-100 int and sends it. The dedup key is a simple tuple comparison. The
system never needs to understand what the raw numbers mean.

Callers normalize to integer percent before calling:
`step_percent = min(100, int(current_ms / duration_ms * 100))`
Many frames map to the same integer and are auto-dropped. Only distinct percent values cost IPC.

**Indeterminate steps (step_percent=None):**

When progress cannot be determined, caller passes `step_percent=None`. The dialog shows a Qt
indeterminate progress bar (`setRange(0, 0)` — the pulsing animation). Dedup still works:
`None == None` so repeated calls with the same step and `step_percent=None` are all dropped after
the first. A caller scanning thousands of directories fires one IPC call and the rest are free.

**Indeterminate → determinate transition and the "preparing" state:**

These are the same problem. A task may start with an unknown amount of preparation (directory
traversal, network probe, etc.) before switching to a countable loop.

Use `step=0` as an explicit preparation sentinel and `total_steps=None` to mean "count not yet
known":

```
# Phase 1 - traversal, count unknown
context.report_step_progress(step=0, total_steps=None,
                              step_title='Scanning...', step_percent=None)
... traverse dirs, collect files ...

# Phase 2 - processing, count now known
for i, f in enumerate(files, start=1):
    context.report_step_progress(step=i, total_steps=len(files),
                                 step_title=basename(f), step_percent=0)
    ... process f ...
    context.report_step_progress(step=i, total_steps=len(files),
                                 step_title=basename(f), step_percent=100)
```

Dialog behavior during transition:
- `total_steps=None`: single indeterminate row with step_title, no step count shown
- First call where `total_steps` becomes an int: dialog switches to step-list layout. The step=0
  preparation row can be shown as a completed preamble or discarded.
- Step transitions (step N → step N+1) always pass the dedup check since `step` changes.

**Collector change:**
- Update `btask_result_collector_i._handle_item` to recognize `btask_status_step_progress` and
  pass it through to `handle_status` without applying `_should_drop_progress` (the 1% drop logic
  only applies to the old type). Since auto-throttling already happened in the worker process,
  every item that reaches the collector is worth delivering.

---

## Phase 2 — New dialog widget in `rmt`

Create `rui_step_progress_dialog` — a custom `QDialog`. Qt has no standard widget for a list of
steps with individual progress bars.

**Layout:**
- Title label at top
- Scrollable area (`QScrollArea` containing `QVBoxLayout`) of step rows
- Each row: `[step number label] [step title label ........] [QProgressBar]`
- Cancel button (optional, controlled by caller)

**Behavior:**
- `update_step(step, total_steps, title, percent)` — creates the row on first call for a given
  step index, updates it on subsequent calls
- Completed steps: progress bar at 100%, label greyed out
- Current step: progress bar animating (or at current percent)
- Steps are never removed, only updated — so the full history is visible

---

## Phase 3 — New dialog entry point in `rui_process_task_dialog`

Add `task_with_step_progress(processor, parent, function, callback, title, args, config, ...)`
alongside existing `task_with_progress`.

- Creates `rui_step_progress_dialog`
- `_task_status_callback` dispatches on type:
  - `btask_status_step_progress` → calls `dialog.update_step(...)`
  - old `btask_status_progress` → ignored (or forwarded to a simple label if needed)
- Existing `task_with_progress` is completely unchanged

---

## Phase 4 — `fdui_transcode_tasks.py` + `fdui_transcode.py`

The motivating case.

**Task changes (`fdui_transcode_tasks.py`):**
- At start of each file: `context.report_step_progress(step=i, total_steps=num_files, step_title=basename, step_percent=0)`
- In ffmpeg callback: `context.report_step_progress(step=i, total_steps=num_files, step_title=basename, step_percent=percent)`
- Remove the now-unnecessary `context.report_progress(0, 100, 0, '')` pre-loop call

**Caller change (`fdui_transcode.py`):**
- Switch from `task_with_progress` to `task_with_step_progress`

---

## Phase 5 — `rui_video_trim_tasks.py` + `fdui_video_trim.py`

Single step with ms-based sub-progress.

**Task changes (`rui_video_trim_tasks.py`):**
- Replace `context.report_progress(0, duration_ms, ...)` with
  `context.report_step_progress(step=1, total_steps=1, step_title='Trimming', step_percent=percent)`
  where `percent = min(100, int(current_ms / duration_ms * 100))`

**Caller change (`fdui_video_trim.py`):**
- Switch from `task_with_progress` to `task_with_step_progress`

---

## Phase 6 — `fdui_face_detect_tasks.py` + `fdui_face_detect.py`

Step-only, no sub-progress.

**Task changes (`fdui_face_detect_tasks.py`):**
- Replace `context.report_progress(1, num_files, i, message)` with
  `context.report_step_progress(step=i, total_steps=num_files, step_title=basename, step_percent=None)`

**Caller changes (`fdui_face_detect.py`):**
- Switch all three `task_with_progress` calls to `task_with_step_progress`

---

## Phase 7 — `fdui_similar_images_tasks.py` + `fdui_similar_images.py`

Same pattern as Phase 6.

**Task changes (`fdui_similar_images_tasks.py`):**
- Replace `context.report_progress(1, num_entries, i, message)` with
  `context.report_step_progress(step=i, total_steps=num_entries, step_title=message, step_percent=None)`

**Caller change (`fdui_similar_images.py`):**
- Switch `task_with_progress` to `task_with_step_progress`

---

## Phase 8 — `fdui_file_tasks.py` + `fdui_file_operations.py`

Mixed: staging/filing loops get step progress; trash operations are indeterminate and can stay on
old `report_progress` or use `report_step_progress` with `step_percent=None` and a single step.

**Task changes (`fdui_file_tasks.py`):**
- Staging loop: `context.report_step_progress(step=index, total_steps=num, step_title='staging', step_percent=None)`
- Filing loop: `context.report_step_progress(step=index, total_steps=num, step_title='filing', step_percent=None)`
- Trash operations (indeterminate): leave on old `report_progress` OR use
  `context.report_step_progress(step=1, total_steps=1, step_title='Moving to trash...', step_percent=None)`

**Caller changes (`fdui_file_operations.py`):**
- Switch applicable `task_with_progress` calls to `task_with_step_progress`

---

## Phase 9 — `fdui_preview_tasks.py` + `fdui_preview.py`

Step-only.

**Task changes (`fdui_preview_tasks.py`):**
- Replace `context.report_progress(1, num_files, i, message)` with
  `context.report_step_progress(step=i, total_steps=num_files, step_title=message, step_percent=None)`

**Caller change (`fdui_preview.py`):**
- Switch `task_with_progress` to `task_with_step_progress`

---

## Phase 10 — `fdui_redgifs.py` (2 usages)

Both are file iteration loops.

**Task changes (`fdui_redgifs.py`):**
- Both `context.report_progress(0, num_files, i, message)` calls replaced with
  `context.report_step_progress(step=i, total_steps=num_files, step_title=message, step_percent=None)`

**Caller changes (`fdui_redgifs.py`):**
- Switch both `task_with_progress` calls to `task_with_step_progress`

---

## Phase 11 — `redgifs_creator_window.py`

Generic iteration.

**Task changes:**
- Replace `context.report_progress(0, maximum, value, message)` with
  `context.report_step_progress(step=value, total_steps=maximum, step_title=message, step_percent=None)`

**Caller change:**
- Switch `task_with_progress` to `task_with_step_progress`

---

## Phase 12 — Retire old interface

Once all usages are on the new interface and tested:

- Remove `report_progress` from `btask_function_context`
- Remove `btask_status_progress` and `btask_progress` dataclasses
- Remove `_should_drop_progress` from `btask_result_collector_i` entirely (new interface always
  uses 0-100 or None so a simple always-pass or clean drop rule can replace it if needed)
- Remove old dispatch path in `rui_process_task_dialog._task_status_callback`
- Remove `task_with_progress` from `rui_process_task_dialog` (or keep as thin wrapper if still useful)
- Remove `rui_progress_dialog` if no longer used

---

## Notes

- Phases 4-11 are independent of each other once Phases 1-3 are complete and can be done in any order
- PyQt6 has no built-in "steps list with progress bars" widget — Phase 2 is a custom widget and is
  the heaviest single phase
- The `_should_drop_progress` modulo bug does not affect the new interface since `step_percent` is
  always a 0-100 integer (no non-uniform timestamp values)
- The `_pump()` contention issue (calling `_pump()` for every progress item in `btask_processor._callback`)
  is a separate bug worth fixing independently: only call `_pump()` when the item is a `btask_result`,
  not a `_btask_status_queue_item`
