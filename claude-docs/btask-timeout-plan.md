# btask Timeout Plan

## Problem

Long-running btask tasks can hang indefinitely — a stuck CD rip (cdparanoia blocked on a bad disc) can run for 24+ hours with no way for the framework to detect or recover.  The framework needs per-task timeouts that:

1. Attempt a soft cancellation first (set the cancelled flag; let the task exit cleanly via `raise_cancelled_if_needed`).
2. Hard-kill the worker process after a grace period if soft cancellation is not acknowledged.
3. Self-heal the pool (replace the killed worker) so subsequent tasks run normally.
4. Produce a `TIMED_OUT` result that flows through the same callback chain as `CANCELLED` and `FAILED`.

---

## New Result State

`btask_result_state.py` — add `TIMED_OUT`:

```python
class btask_result_state(checked_enum):
  SUCCESS   = 'success'
  FAILED    = 'failed'
  CANCELLED = 'cancelled'
  TIMED_OUT = 'timed_out'    # ← new
```

---

## Config Change — `btask_config`

Add two optional fields:

```python
@dataclasses.dataclass
class btask_config:
  category:           str
  priority:           str          = 'medium'
  limit:              int          = 3
  debug:              bool         = False
  timeout_seconds:    Optional[int] = None   # ← new: None means no timeout; minimum 2
  kill_grace_seconds: int           = 5      # ← new: seconds between SIGTERM and SIGKILL; minimum 1
```

Both fields are `int`.  Sub-second precision is unnecessary: `timeout_seconds` is bounded by the 1-second watchdog poll window, and `kill_grace_seconds` is a coarse human-scale delay — if a process has not responded to SIGTERM within a whole number of seconds it is not going to.  Float would imply a precision that serves no practical purpose.

The minimum enforced value for `timeout_seconds` is **2 seconds**: a value of 1 falls within the margin of the 1-second poll cycle and could fire immediately or up to 2 seconds late.  The minimum for `kill_grace_seconds` is **1 second**.

The 4-tuple shorthand `('category', 'priority', limit, debug)` used in tests and `add_task` continues to work; the new fields have defaults and are only set via keyword arguments or a 6-tuple.

---

## New Internal Message — `_btask_task_started_item`

The timeout watchdog needs to know when a task started and in which worker process, so it can kill it by PID.  Add a new internal message that the worker puts on the result queue immediately before calling `task.function()`:

```python
# lib/bes/btask/_btask_task_started_item.py
from collections import namedtuple
_btask_task_started_item = namedtuple('_btask_task_started_item', 'task_id, pid')
```

Analogous to `_btask_status_queue_item`.

---

## New Exception — `btask_timeout_error`

```python
# lib/bes/btask/btask_timeout_error.py
class btask_timeout_error(Exception):
  def __init__(self, message, timeout_seconds=None):
    super().__init__(message)
    self.timeout_seconds = timeout_seconds
```

Analogous to `btask_cancelled_error`.  Not raised inside the worker (the worker may be stuck and unable to raise anything); used internally to represent the timeout condition when building the result.

---

## Changes to `btask_process`

Before calling `task.function(context, task.args)`, send the started notification:

```python
result_queue.put(_btask_task_started_item(task.task_id, os.getpid()))
# ... existing call ...
result_data = task.function(context, task.args)
```

No other changes to `btask_process`.

---

## Changes to `btask_process_pool`

`btask_process_pool` gains a **timeout watchdog thread** and tracking state.

### New state

```python
self._task_pid_map: dict[int, int]              # task_id → worker pid
self._task_start_time_map: dict[int, datetime]  # task_id → start time
self._task_config_map: dict[int, btask_config]  # task_id → config (for timeout values)
self._timed_out_task_ids: set[int]              # task_ids that have had a timeout triggered
self._task_pid_map_lock: threading.Lock
```

### Watchdog thread cost

The watchdog thread blocks in `_stop_event.wait(timeout=1.0)` — it is parked by the OS and uses zero CPU while sleeping.  When it wakes each second it acquires a lock, iterates the start-time dict (skipping tasks with `timeout_seconds=None` or not yet expired), and goes back to sleep.  This is microseconds of work per second regardless of how many tasks are queued or whether any timeouts are ever configured.

### Handling `_btask_task_started_item`

In `_result_thread_main`, add a branch for the new message type:

```python
elif isinstance(item, _btask_task_started_item):
  with self._task_pid_map_lock:
    self._task_pid_map[item.task_id] = item.pid
    self._task_start_time_map[item.task_id] = datetime.now()
```

When a task result arrives (success/failed/cancelled/timed_out), clean up the maps:

```python
with self._task_pid_map_lock:
  self._task_pid_map.pop(result.task_id, None)
  self._task_start_time_map.pop(result.task_id, None)
  self._task_config_map.pop(result.task_id, None)
  self._timed_out_task_ids.discard(result.task_id)
```

### Result interception — always TIMED_OUT

When a timeout is triggered for a task, `task_id` is added to `_timed_out_task_ids` immediately (before either the soft-cancel or hard-kill path completes).  In `_result_thread_main`, any result arriving for a task in that set is **converted to `TIMED_OUT`** before being forwarded to the callback, and any second result for the same task_id is suppressed.

This means the result is always `TIMED_OUT` regardless of whether the worker exited cleanly via soft cancellation or was hard-killed — the distinction between the two exit mechanisms is an implementation detail that callers should not need to handle separately.

```python
# in _result_thread_main, after receiving a real result for a task_id:
with self._task_pid_map_lock:
  if result.task_id in self._timed_out_task_ids:
    if result.state == btask_result_state.CANCELLED:
      # soft cancel worked — convert to TIMED_OUT, cancel the pending grace timer
      result = result._replace(state=btask_result_state.TIMED_OUT)
      self._cancel_grace_timer(result.task_id)
    # second result for a hard-killed task — suppress (TIMED_OUT already emitted)
    elif result.state == btask_result_state.TIMED_OUT:
      pass  # already handled by _emit_timed_out_result
```

### Storing config per task

`btask_process_pool.add_task(task, callback)` already receives the `btask_task` which contains the config.  Store it:

```python
with self._task_pid_map_lock:
  self._task_config_map[task.task_id] = task.config
```

### Timeout Watchdog Thread

Polls every 1 second.  Effective timeout granularity is ±1 second — a task with `timeout_seconds=5` fires between 5.0 and 6.0 seconds after it starts depending on where in the poll cycle the task began.  This is why `timeout_seconds` has a minimum of 2.

```python
def _timeout_watchdog_main(self):
  while not self._stop_event.is_set():
    self._stop_event.wait(timeout=1.0)
    self._check_timeouts()

def _check_timeouts(self):
  with self._task_pid_map_lock:
    now = datetime.now()
    for task_id, start_time in list(self._task_start_time_map.items()):
      config = self._task_config_map.get(task_id)
      if config is None or config.timeout_seconds is None:
        continue
      elapsed = (now - start_time).total_seconds()
      if elapsed >= config.timeout_seconds:
        self._handle_timeout(task_id, config)
```

### Timeout Handling Sequence

```python
def _handle_timeout(self, task_id, config):
  # Must be called with _task_pid_map_lock held
  pid = self._task_pid_map.get(task_id)
  if pid is None:
    return  # already completed

  # Mark as timed out before releasing anything — ensures result interception is active
  self._timed_out_task_ids.add(task_id)

  # 1. Soft cancel — set cancelled flag via the in-progress task's cancelled_value
  self._timeout_callback(task_id)  # processor.timeout(task_id) — see below

  # 2. Start a grace period timer that hard-kills if the worker does not exit cleanly
  grace = config.kill_grace_seconds
  timer = threading.Timer(grace, self._hard_kill, args=(task_id, pid))
  timer.daemon = True
  timer.start()
  self._grace_timers[task_id] = timer
```

```python
def _hard_kill(self, task_id, pid):
  try:
    os.kill(pid, signal.SIGTERM)
  except ProcessLookupError:
    return  # already exited during grace period — soft cancel worked; result already converted
  time.sleep(0.5)
  try:
    os.kill(pid, signal.SIGKILL)
  except ProcessLookupError:
    pass
  # Synthesize TIMED_OUT result and put it on the result queue
  self._emit_timed_out_result(task_id)
  # Replace the dead worker process
  self._respawn_worker()
```

```python
def _cancel_grace_timer(self, task_id):
  # Called (with lock held) when soft cancel delivered the result first
  timer = self._grace_timers.pop(task_id, None)
  if timer is not None:
    timer.cancel()
```

### Synthesizing the TIMED_OUT Result

Only reached via the hard-kill path (soft cancel already converted the worker's CANCELLED result in `_result_thread_main`).

```python
def _emit_timed_out_result(self, task_id):
  with self._task_pid_map_lock:
    pid = self._task_pid_map.pop(task_id, 0)
    start_time = self._task_start_time_map.pop(task_id, datetime.now())
    self._task_config_map.pop(task_id, None)
  end_time = datetime.now()
  metadata = btask_result_metadata(pid=pid, add_time=start_time,
                                   start_time=start_time, end_time=end_time)
  result = btask_result(task_id=task_id,
                        state=btask_result_state.TIMED_OUT,
                        data=None,
                        metadata=metadata,
                        error=None,
                        args={})
  self._process_result_queue.put(result)
```

### Worker Respawn

```python
def _respawn_worker(self):
  # Start a new btask_process to replace the killed one
  new_process = btask_process(f'{self._name}_respawn',
                               self._input_queue,
                               self._process_result_queue)
  new_process.start()
  # Track it like the original pool processes
```

---

## Changes to `btask_processor`

Add `timeout(task_id)` method, called by the pool's timeout watchdog:

```python
def timeout(self, task_id):
  'Called by the process pool when a task exceeds its timeout; triggers soft cancellation.'
  with self._lock:
    item = self._in_status_queue.find_by_task_id(task_id)
    if item is not None:
      item.cancelled_value.value = True  # soft signal; worker may or may not see it
```

The pool's hard-kill fires after the grace period regardless of whether the worker acknowledged the soft signal.

---

## Changes to `btask_result_collector_i`

Handle `_btask_task_started_item` routing — pass it to `btask_process_pool` rather than to the processor.  Since the pool already handles this in `_result_thread_main`, no change to the collector is needed if the started item is handled within the pool's result thread before it reaches the collector.

---

## Files Modified / Added

| File | Change |
|---|---|
| `btask_result_state.py` | Add `TIMED_OUT = 'timed_out'` |
| `btask_config.py` | Add `timeout_seconds` (int), `kill_grace_seconds` (int) fields |
| `btask_process.py` | Put `_btask_task_started_item` on result queue before calling function |
| `btask_process_pool.py` | Add watchdog thread, pid/start_time/config tracking, hard-kill, respawn, result interception |
| `btask_processor.py` | Add `timeout(task_id)` method |
| `_btask_task_started_item.py` | New — namedtuple `(task_id, pid)` |
| `btask_timeout_error.py` | New — exception class |

---

## Unit Tests

New test file: `tests/lib/bes/btask/test_btask_timeout.py`

All tests use `btask_processor_tester_py` (the full stack) unless testing a layer directly.  Timeouts must be `int` and at least 2 seconds; grace periods can be float.  Tests use the minimum viable values to keep the suite reasonably fast while respecting the 2-second minimum constraint.

### Helper task functions

```python
@classmethod
def _fn_sleep_forever(clazz, context, args):
  'Simulates a stuck task — ignores cancellation, sleeps effectively forever.'
  time.sleep(3600)
  return {}

@classmethod
def _fn_sleep_with_cancel_check(clazz, context, args):
  'Simulates a well-behaved long task — checks cancellation periodically.'
  for _ in range(100):
    time.sleep(0.050)
    context.raise_cancelled_if_needed('cancelled')
  return {}

@classmethod
def _fn_fast(clazz, context, args):
  'Completes quickly — used to verify pool self-heals after a timeout.'
  return {'done': True}
```

### Test cases

**`test_timeout_result_state`**
Single task that sleeps forever, `timeout_seconds=2`.  Assert result state is `'timed_out'`.

**`test_timeout_completes_before_deadline`**
Single task that sleeps 0.1s, `timeout_seconds=5`.  Assert result state is `'success'`.  Verifies timeout does not fire on tasks that complete normally.

**`test_timeout_callback_called`**
Single stuck task, `timeout_seconds=2`.  Assert that the task callback is called exactly once with a `'timed_out'` result.

**`test_timeout_soft_cancel_respected`**
Task uses `_fn_sleep_with_cancel_check` (checks cancellation every 50 ms).  `timeout_seconds=2`.  Assert result state is `'timed_out'` (not `'cancelled'`) — confirms the soft-cancel-to-TIMED_OUT conversion works.  Assert task exits promptly after the timeout fires (well within the grace period), confirming no hard kill was needed.

**`test_timeout_hard_kill`**
Task uses `_fn_sleep_forever` (ignores cancellation).  `timeout_seconds=2`, `kill_grace_seconds=1`.  Assert result state is `'timed_out'`.  Assert wall time from task start to result callback is < `timeout_seconds + kill_grace_seconds + margin`.  Verifies the hard kill fires.

**`test_pool_self_heals_after_timeout`**
Submit a stuck task (`timeout_seconds=2`, `kill_grace_seconds=1`).  After it times out, submit a fast task to the same pool.  Assert fast task completes with state `'success'`.  Verifies pool respawned a worker.

**`test_multiple_tasks_one_times_out`**
Submit 3 tasks: two fast tasks and one stuck task (`timeout_seconds=2`).  Assert the two fast tasks succeed and the stuck task is `'timed_out'`.  Verifies timeout of one task does not interfere with others.

**`test_multiple_tasks_all_time_out`**
Submit 3 stuck tasks each with `timeout_seconds=2`.  Assert all 3 results are `'timed_out'`.  Assert pool self-heals (submit a 4th fast task after, assert success).

**`test_timeout_metadata`**
Stuck task, `timeout_seconds=2`.  On `'timed_out'` result, assert `result.metadata.duration >= timedelta(seconds=2)`.

**`test_no_timeout_set`**
Task with `timeout_seconds=None` that runs for 0.5s.  Assert result is `'success'` — no timeout fires.

**`test_timeout_waiting_task`**
Use a pool with `limit=1`.  Submit a stuck task followed by a second task with `timeout_seconds=2`.  The second task is in the waiting queue when its timeout fires (it hasn't started yet).  Assert second task result is `'timed_out'`.  (Tasks in the waiting queue have no worker process; the `timeout()` method handles this via cancellation, and the result is converted to `TIMED_OUT` via the same interception path.)

**`test_timeout_in_progress_multiple_pools`**
Use dedicated categories to create two separate pools.  Submit a stuck task to each, each with `timeout_seconds=2`.  Assert both come back `'timed_out'` and both pools self-heal.

---

## Notes and Edge Cases

- **Always TIMED_OUT**: once a timeout is triggered for a task, the result is always `TIMED_OUT` regardless of how the task exits.  The `_timed_out_task_ids` set is the gate.  Any `CANCELLED` result arriving for a task in that set is converted to `TIMED_OUT` and the pending grace timer is cancelled.  Any second result (from the hard-kill path after the soft-cancel already delivered a result) is suppressed.

- **Waiting queue timeout**: tasks in the waiting queue have no worker process.  The `timeout()` method sets the cancelled flag, which causes the processor to emit a `CANCELLED` result when it dequeues the task.  That result is then converted to `TIMED_OUT` by the same interception in `_result_thread_main`.  No hard kill or respawn is needed.

- **Process pool sizing**: after a hard kill the pool has one fewer worker until `_respawn_worker()` runs.  During the gap (SIGKILL to respawn), tasks may queue up — this is acceptable.  The respawn happens synchronously within `_hard_kill` before returning.

- **Watchdog granularity**: the effective fire time for a timeout is between `timeout_seconds` and `timeout_seconds + 1` seconds after the task starts (the ±1 s poll window).  This is why `timeout_seconds` is an `int` with a minimum of 2 — a value of 1 would be within the noise of the poll cycle.
