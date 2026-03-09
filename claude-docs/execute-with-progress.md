# execute_with_progress

## What it is

A thin classmethod added to `execute` in `lib/bes/system/execute.py` that wraps the existing `non_blocking=True` + `output_function` machinery with a pluggable `line_parser` callable. Motivated by the recurring pattern of tools (SongKong, ffmpeg, etc.) that emit structured progress on stdout/stderr one line at a time.

The existing `execute.execute(non_blocking=True, output_function=fn)` already does the hard work of the readline loop. `execute_with_progress` adds one layer on top: it routes each line through a caller-supplied parser, collects the parsed events, and returns them alongside the normal `execute_result`.

---

## Interface

```python
execute.execute_with_progress(
  args,
  line_parser,      # callable(stdout_line: str, stderr_line: str) -> Any | None
  progress_cb=None, # callable(event: Any) -> None  (optional, called live per event)
  **kwargs          # forwarded verbatim to execute.execute()
) -> execute_progress_result
```

### `line_parser`

Called once per readline tick with the current `(stdout_line, stderr_line)` pair — the same pair the existing `output_function` receives via the `_output` namedtuple, unpacked for convenience.

- Return a value (any type) to record it as an event.
- Return `None` to silently skip the line (no event recorded, no callback fired).

The parser is the caller's responsibility. `execute_with_progress` does not interpret the return value.

### `progress_cb`

Optional. Called immediately (live, during the run) for each non-`None` event. Useful for printing progress to the terminal. If omitted, events are still collected and available in the result.

### `**kwargs`

All keyword arguments are forwarded to `execute.execute()`. `non_blocking=True` is set internally and must not be passed by the caller (it will raise). All other `execute.execute` options (`cwd`, `env`, `stderr_to_stdout`, `raise_error`, etc.) are available.

### Return value: `execute_progress_result`

A namedtuple with two fields:

```python
execute_progress_result(result, events)
```

- **`result`** — the underlying `execute_result` (stdout, stderr, exit_code, command). Unchanged from what `execute.execute` would return.
- **`events`** — list of all non-`None` values returned by `line_parser`, in order.

---

## Internal implementation

```python
_execute_progress_result = namedtuple('_execute_progress_result', 'result, events')

@classmethod
def execute_with_progress(clazz, args, line_parser, progress_cb=None, **kwargs):
  check.check_callable(line_parser)
  check.check_callable(progress_cb, allow_none=True)
  if 'non_blocking' in kwargs:
    raise ValueError('non_blocking is set internally by execute_with_progress')

  events = []
  def _output_function(output):
    event = line_parser(output.stdout, output.stderr)
    if event is not None:
      events.append(event)
      if progress_cb:
        progress_cb(event)

  result = clazz.execute(args, non_blocking=True, output_function=_output_function, **kwargs)
  return _execute_progress_result(result, events)
```

That's the entire implementation. `_poll_process` in `execute.py` already handles the readline loop, stdout/stderr separation, and `stderr_to_stdout` mode. This method adds nothing to that machinery.

---

## Usage example (SongKong)

```python
from bes.system.execute import execute
from rmusic.songkong.rmusic_songkong_progress import rmusic_songkong_progress

def _on_event(event):
  if event.kind == 'progress':
    print(f'  {event.counts}')

rv = execute.execute_with_progress(
  ['/Applications/SongKong.app/Contents/MacOS/SongKong', '-m', album_dir],
  line_parser = rmusic_songkong_progress.parse_line,
  progress_cb = _on_event,
  env = {'HOME': tmp_home},
  raise_error = False,
)
summary = {e.key: e.value for e in rv.events if e.kind == 'summary'}
```

---

## Unit tests

Test file: `tests/lib/bes/system/test_execute_with_progress.py`

Tests use inline Python scripts as mock subprocesses (cross-platform, no shell script required). Pattern follows `test_execute.py` — use `self.make_temp_file(content=..., perm=0o0755, suffix='.py')` and `unit_test` base class.

### Test cases

**`test_events_collected`**
Mock script prints 3 known lines. Parser returns a string event for each. Assert `rv.events == ['line1', 'line2', 'line3']`.

**`test_none_filtered`**
Parser returns `None` for lines containing `'skip'`, event for others. Mock script prints a mix. Assert only non-skip lines appear in `rv.events`.

**`test_progress_cb_called_live`**
Append to a list inside `progress_cb`. Assert the list matches `rv.events` after the run — verifying the callback fires during execution, not after.

**`test_progress_cb_not_called_for_none`**
Parser returns `None` for every line. Assert `progress_cb` is never called and `rv.events` is empty.

**`test_result_has_execute_result`**
Assert `rv.result.exit_code == 0`, `rv.result.stdout` contains expected content — verifying the underlying `execute_result` is passed through unmodified.

**`test_stderr_lines_reach_parser`**
Mock script writes to stderr. Pass `stderr_to_stdout=True`. Assert parser receives those lines (via `stdout_line`) and events are collected correctly.

**`test_non_blocking_not_allowed_in_kwargs`**
Assert that passing `non_blocking=True` as a kwarg raises `ValueError`.

**`test_parser_receives_correct_stdout_stderr`**
Mock script writes distinct strings to stdout and stderr (without `stderr_to_stdout`). Parser records `(stdout_line, stderr_line)` tuples. Assert the stdout and stderr values land in the correct argument position.

**`test_empty_output`**
Mock script prints nothing and exits 0. Assert `rv.events == []` and `rv.result.exit_code == 0`.

**`test_high_line_count`**
Mock script prints 1000 lines. Assert all 1000 events collected — sanity check that the readline loop doesn't drop lines.

---

## Files changed

- `lib/bes/system/execute.py` — add `_execute_progress_result` namedtuple and `execute_with_progress` classmethod
- `tests/lib/bes/system/test_execute_with_progress.py` — new test file (10 tests above)

No other files change. The `execute_result` type is unchanged.
