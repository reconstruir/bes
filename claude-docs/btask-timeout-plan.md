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
  category:         str
  priority:         str   = 'medium'
  limit:            int   = 3
  debug:            bool  = False
  timeout_seconds:  Optional[float] = None   # ← new: None means no timeout
  kill_grace_seconds: float = 5.0            # ← new: seconds between SIGTERM and SIGKILL
```

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
self._task_pid_map_lock: threading.Lock
```

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
```

### Storing config per task

`btask_process_pool.add_task(task, callback)` already receives the `btask_task` which contains the config.  Store it:

```python
with self._task_pid_map_lock:
  self._task_config_map[task.task_id] = task.config
```

### Timeout Watchdog Thread

Runs every 1 second.  For each tracked in-progress task:

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

  # 1. Soft cancel — set cancelled flag via the in-progress task's cancelled_value
  #    (processor sets this; watchdog calls back into processor)
  self._timeout_callback(task_id)  # processor.timeout(task_id) — see below

  # 2. Start a grace period timer that hard-kills if needed
  grace = config.kill_grace_seconds
  timer = threading.Timer(grace, self._hard_kill, args=(task_id, pid))
  timer.daemon = True
  timer.start()
```

```python
def _hard_kill(self, task_id, pid):
  try:
    os.kill(pid, signal.SIGTERM)
  except ProcessLookupError:
    return  # already exited during grace period — good
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

### Synthesizing the TIMED_OUT Result

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
| `btask_config.py` | Add `timeout_seconds`, `kill_grace_seconds` fields |
| `btask_process.py` | Put `_btask_task_started_item` on result queue before calling function |
| `btask_process_pool.py` | Add watchdog thread, pid/start_time/config tracking, hard-kill, respawn |
| `btask_processor.py` | Add `timeout(task_id)` method |
| `_btask_task_started_item.py` | New — namedtuple `(task_id, pid)` |
| `btask_timeout_error.py` | New — exception class |

---

## Unit Tests

New test file: `tests/lib/bes/btask/test_btask_timeout.py`

All tests use `btask_processor_tester_py` (the full stack) unless testing a layer directly.  Short sleep times (100–500 ms) and short timeouts (200–500 ms) keep the suite fast.

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
Single task that sleeps forever, timeout=0.3s.  Assert result state is `'timed_out'`.

**`test_timeout_completes_before_deadline`**
Single task with a 100 ms sleep and timeout=2s.  Assert result state is `'success'`.  Verifies timeout does not fire on tasks that complete normally.

**`test_timeout_callback_called`**
Single stuck task, timeout=0.3s.  Assert that the task callback is called exactly once with a `'timed_out'` result.

**`test_timeout_soft_cancel_respected`**
Task uses `_fn_sleep_with_cancel_check` (checks cancellation every 50 ms).  Timeout=0.2s.  Assert result state is `'timed_out'` and that the task exits within a reasonable time after the timeout fires (≤ 500 ms after deadline) — i.e., the soft signal worked and no hard kill was needed.

**`test_timeout_hard_kill`**
Task uses `_fn_sleep_forever` (ignores cancellation).  Timeout=0.3s, grace=0.3s.  Assert result state is `'timed_out'`.  Assert wall time from task start to result callback is < timeout + grace + margin (1.5s total).  Verifies the hard kill fires.

**`test_pool_self_heals_after_timeout`**
Submit a stuck task (timeout=0.3s, grace=0.3s).  After it times out, submit a fast task to the same pool.  Assert fast task completes with state `'success'`.  Verifies pool respawned a worker.

**`test_multiple_tasks_one_times_out`**
Submit 3 tasks: two fast tasks and one stuck task (timeout=0.3s).  Assert the two fast tasks succeed and the stuck task is `'timed_out'`.  Verifies timeout of one task does not interfere with others.

**`test_multiple_tasks_all_time_out`**
Submit 3 stuck tasks each with timeout=0.3s.  Assert all 3 results are `'timed_out'`.  Assert pool self-heals (submit a 4th fast task after, assert success).

**`test_timeout_metadata`**
Stuck task, timeout=0.3s.  On `'timed_out'` result, assert `result.metadata.duration >= timedelta(seconds=0.3)`.

**`test_no_timeout_set`**
Task with no `timeout_seconds` (None) that runs for 500 ms.  Assert result is `'success'` — no timeout fires.

**`test_timeout_waiting_task`**
Use a pool with `limit=1`.  Submit a stuck task followed by a second task with timeout=0.2s.  The second task is in the waiting queue when its timeout fires (it hasn't started yet).  Assert second task result is `'timed_out'`.  (This case is handled by `btask_processor.cancel(task_id)` via the same `timeout()` call — tasks in the waiting queue need no hard kill since no process is running them.)

**`test_timeout_in_progress_multiple_pools`**
Use dedicated categories to create two separate pools.  Submit a stuck task to each, each with timeout=0.3s.  Assert both come back `'timed_out'` and both pools self-heal.

---

## Notes and Edge Cases

- **Task completes during grace period**: if the worker exits cleanly (soft cancel worked) between the SIGTERM and the grace period timer firing, `_hard_kill` catches `ProcessLookupError` and returns without emitting a duplicate result.  The result already in flight (CANCELLED from the worker) takes precedence.  The maps must be cleaned up when either result arrives first — use a lock and check-and-remove pattern to prevent double-emission.

- **Double result prevention**: since both the soft-cancel path (worker emits `CANCELLED`) and the hard-kill path (pool emits `TIMED_OUT`) could produce a result for the same task_id, the pool must track whether a result has already been emitted for a task_id and suppress duplicates.  A `_timed_out_task_ids: set` protected by the lock is sufficient.

- **Waiting queue timeout**: tasks in the waiting queue have no worker process. The `timeout()` method calls `processor.cancel(task_id)` which handles this case already — the task is removed from the waiting queue and a CANCELLED result is emitted. For waiting-queue timeouts we emit `TIMED_OUT` instead of `CANCELLED` by adding a `timed_out=True` flag to the cancel call path, or by re-using cancel and overriding the state in the synthesized result.

- **Process pool sizing**: after a hard kill the pool has one fewer worker until `_respawn_worker()` runs.  During the gap (SIGKILL to respawn), tasks may queue up — this is acceptable.  The respawn should happen synchronously within `_hard_kill` before returning.
