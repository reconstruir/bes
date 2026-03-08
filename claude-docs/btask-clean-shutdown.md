# btask Clean Shutdown Plan

## Problem Summary

Two related failure modes, both rooted in the same underlying causes:

1. **CLI Ctrl+C** — hitting Ctrl+C leaves worker processes running (holding open CD drives, whipper subprocesses, network ports, etc.).
2. **GUI quit hangs** — calling `processor.stop()` from the UI thread blocks indefinitely if any task is still running.
3. **GUI Ctrl+C** — same as CLI Ctrl+C; the SIGINT bypasses the GUI's quit handler entirely.

---

## Root Cause Analysis

### Root Cause 1 — Worker processes are non-daemon

`btask_process.start()` creates a `multiprocessing.Process` without `daemon=True`.  Non-daemon child processes are **not automatically killed** when the parent process exits for any reason (normal exit, uncaught exception, Ctrl+C).  Python's `multiprocessing` atexit handler tries to `join()` them — which blocks — but on an abnormal exit the cleanup may not even run, and the workers just become orphans.

**Concrete effect:** after Ctrl+C, all worker processes continue executing their current tasks (whipper ripping, ffmpeg transcoding, etc.) indefinitely.  The parent process may hang (if atexit fires and tries to join), or it may exit and leave the workers as zombies/orphans depending on platform timing.

The `multiprocessing.Manager()` server process has the same problem — it owns the shared queues and Value objects.  If it outlives the workers (or is cleaned up before them), the workers crash trying to use its queues.

### Root Cause 2 — `stop()` has no way to interrupt in-progress tasks

`btask_process_pool._processes_stop()` sends one `None` sentinel per worker on `_input_queue`:

```python
for _ in processes:
    input_queue.put(None)   # termination sentinel
for process in processes:
    process.join()          # blocks here
```

The sentinel only works if the worker is **idle** — blocked on `input_queue.get()`.  If the worker is inside `task.function(context, task.args)` running a long job, it will never read the sentinel.  `process.join()` blocks forever.

**Nothing in `stop()` signals the running task to stop.**  `cancelled_value.value` is not set, no signal is sent to the process, and there is no timeout on `join()`.

This is why the GUI hangs on quit: `processor.stop()` → `pool.stop()` → `process.join()` → blocked waiting for tasks that run for hours.

### Root Cause 3 — No SIGINT handler

Neither `btask_processor` nor any caller installs a `SIGINT` (Ctrl+C) signal handler.  When the user hits Ctrl+C:

- The main thread (blocked in `main_loop_start()` → `queue.get()`) receives `KeyboardInterrupt`
- The exception propagates up the call stack unhandled
- `processor.stop()` is **never called**
- Workers are orphaned (Root Cause 1) since no cleanup runs

For GUI apps, SIGINT is usually handled by the Qt event loop which raises a quit event, but if the quit path calls `processor.stop()` it hits Root Cause 2.

### Root Cause 4 — Manager process not explicitly shut down

`btask_processor` calls `multiprocessing.Manager()` but never calls `manager.shutdown()` in `stop()`.  The Manager server process (which owns the shared queues, locks, and Value objects) leaks.  On crash it becomes an orphan along with the workers.

---

## What "dangling mess" looks like in practice

After an abnormal exit:

| Process | State | Resources held |
|---|---|---|
| Worker processes (1 per pool worker) | Running or blocked | whipper subprocess, open CD device, partial output files |
| whipper subprocesses (children of workers) | Running | exclusive CD drive access, accparanoia |
| Manager server process | Running | shared memory for queues/locks |

Because whipper holds the CD drive exclusively, subsequent rip attempts will fail even after restarting the app.  On Linux this requires a manual `eject` or device reset.

---

## Plan

### Change 1 — Make worker processes daemon

**File:** `btask_process.py`

Add `daemon=True` to the `multiprocessing.Process` constructor in `start()`:

```python
self._process = multiprocessing.Process(target = self._process_main,
                                        name = self._data.name,
                                        args = ( encoded_task_data, ),
                                        daemon = True)
```

**Effect:** when the parent process exits for any reason (normal, exception, signal), the OS automatically kills all daemon child processes.  This is the single most impactful fix — it eliminates orphaned workers for both the crash and the normal-exit cases.

**Trade-off:** daemon processes cannot themselves spawn child processes (Python restriction).  Workers do not currently spawn children directly (whipper is spawned from the worker, which counts as a grandchild process).  This is fine — the restriction only prevents daemon processes from calling `multiprocessing.Process.start()`.  `subprocess.Popen` (used for whipper) is not affected.

**Note on grandchild processes (whipper):** making the worker daemon kills the worker but does NOT automatically kill whipper (a grandchild spawned via `subprocess.Popen`).  Whipper becomes an orphan adopted by init/systemd.  This is partially addressed by Change 3 (SIGTERM propagation) and should be handled at the task level (`rmusic_whipper.rip()` should use `process.terminate()` in a `finally` block).

### Change 2 — `stop()` cancels in-progress tasks before joining

**File:** `btask_processor.py`

`stop()` should cancel all pending and in-progress tasks, wait a grace period for soft cancel to work, then hard-kill any remaining workers, before finally joining.

New `stop(grace_seconds=5)` sequence:

1. **Stop the watchdog** (existing).
2. **Cancel all waiting tasks** — iterate `_waiting_queue` for all categories; for each item, call `_cancel_waiting_item_i(item)` (same logic as `cancel()` for waiting items but without emitting results since we're shutting down and nobody is listening).
3. **Soft-cancel all in-progress tasks** — iterate `_in_status_queue`; set `cancelled_value.value = True` for each.
4. **Delegate to pool** — call `pool.stop(grace_seconds)` for each pool.
5. **Shut down the manager** — call `self._manager.shutdown()`.

New `btask_process_pool.stop(grace_seconds)` sequence:

1. Send stop sentinel to result thread (`_process_result_queue.put(None)`), join result thread.
2. For each worker process:
   a. Send `None` sentinel to `_input_queue` (in case it's between tasks and idle).
   b. `process.join(timeout=grace_seconds)` — give soft cancel a chance to work.
   c. If `process.is_alive()` after the timeout: `process.kill()` (SIGKILL).
   d. `process.join()` (will return immediately after kill).
3. Clear `self._processes`.

`grace_seconds=5` is the default: long enough for well-behaved tasks to notice `cancelled_value` and exit cleanly, short enough that the app does not hang for more than 5 seconds on quit.

**GUI responsiveness:** `processor.stop(grace_seconds=5)` should be called from a background thread so the GUI event loop stays alive during the grace period.  The UI can show a "shutting down…" indicator.

### Change 3 — SIGINT handler for CLI apps

**File:** new `btask_signal_handler.py` (or handled at the application level)

For CLI apps using `btask_processor_tester_py` or calling `main_loop_start()` directly:

```python
import signal

def _sigint_handler(sig, frame, processor):
    processor.stop(grace_seconds=3)
    raise SystemExit(1)

signal.signal(signal.SIGINT, lambda s, f: _sigint_handler(s, f, processor))
```

This converts Ctrl+C from "abrupt exit" to "graceful shutdown followed by exit".

For rmusic's TUI (`rmusic_whipper_tui`), the SIGINT handler is already flagged as a future feature in RIPPER.md.  The handler there should additionally kill any whipper subprocess in flight (via `try/finally` in `rmusic_whipper.rip()`).

For GUI apps, SIGINT is typically handled by the Qt signal-slot mechanism; the above is not needed.  The "quit from menu" path already leads to `processor.stop()` — Change 2 makes that path non-blocking.

### Change 4 — Manager shutdown in `stop()`

**File:** `btask_processor.py`

At the end of `stop()`, after all pools are stopped, call:

```python
self._manager.shutdown()
```

This cleanly terminates the manager server process and releases its resources (shared memory, sockets).

---

## Summary of Changes

| File | Change |
|---|---|
| `btask_process.py` | Add `daemon=True` to worker process constructor |
| `btask_process_pool.py` | `stop(grace_seconds)`: join with timeout, kill survivors |
| `btask_processor.py` | `stop(grace_seconds)`: cancel all tasks before delegating to pools; call `manager.shutdown()` |
| `rmusic_whipper.rip()` | `try/finally` to kill whipper subprocess on exit (at application level, not btask) |

---

## What each fix addresses

| Issue | Fix |
|---|---|
| CLI Ctrl+C leaves workers running | Change 1 (daemon) + Change 3 (SIGINT handler) |
| GUI quit hangs on `stop()` | Change 2 (cancel + kill with timeout) |
| GUI Ctrl+C leaves workers running | Change 1 (daemon) |
| Manager process leaks | Change 4 (manager.shutdown) |
| Whipper grandchild orphaned on crash | application-level try/finally (RIPPER.md future feature) |

---

## Notes

- **Order matters in `stop()`**: cancel all tasks first (so workers finish quickly), then join with a timeout, then kill.  Joining before cancelling is the bug in the current code.
- **grace_seconds is a hint, not a guarantee**: if a task is in a non-interruptible kernel sleep (rare), SIGKILL is the backstop.
- **Respawned workers** (from the timeout path): `_respawn_worker()` appends to `self._processes`.  `stop()` iterates `self._processes`, so respawned workers are covered automatically.
- **Result thread during stop**: the result thread is stopped (by sentinelling `_process_result_queue`) before joining workers.  Any results produced by workers during the grace period are dropped.  This is acceptable — we're shutting down.
