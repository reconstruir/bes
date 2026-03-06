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

The throttle must live in the worker process — in `report_step_progress` itself — not in the
collector. Dropping at the collector side is too late: the expensive Manager Queue IPC `put()` has
already happened. Dropping in the worker process costs nothing.

Dedup rule: drop the call (zero IPC) if `(step, step_percent) == last_reported`. Always pass if
either `step` or `step_percent` changed. Step transitions (N→N+1) always pass even when both
start at `step_percent=0`.

State added to `btask_function_context`:
- `_last_step_report = None` — tuple `(step, step_percent)` of last call that was not dropped
- `_step_drop_count = 0` — consecutive drop counter for warning

Warning log: when `_step_drop_count` reaches a threshold (e.g. 100), log once:
`"report_step_progress: auto-throttled {n} identical calls for step {step} — caller is reporting
too frequently, consider reducing call frequency"`. Reset `_step_drop_count = 0` when a
non-duplicate passes.

This means callers can call `report_step_progress` on every ffmpeg frame (thousands/second) and
the system remains efficient. The warning tells them when they are excessive, but the system never
overloads regardless.

**Rounding note:** Callers must normalize to integer percent (0-100) before calling, e.g.:
`step_percent = min(100, int(current_ms / duration_ms * 100))`. Many frames will map to the same
integer and be auto-dropped. This is the desired behavior — only distinct percent values cause IPC.

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
