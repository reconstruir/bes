# execute_with_progress

> **Status**: engine (`execute.execute_with_progress`) already implemented.
> ABC layer (`system_command_with_progress` class) and rsync wiring are not yet implemented.
> `claude-docs/execute-with-progress-new.md` superseded by this document — delete it.

---

## Architecture overview

Two complementary layers. The engine is the low-level primitive; the ABC is a
higher-level convention for commands already in the `system_command` hierarchy.

```
execute.execute_with_progress()          ← engine: low-level, always available
        ↑
        used by
        ↑
system_command_with_progress  (ABC)      ← convention for system_command subclasses
        ↑
        inherited by
        ↑
bf_rsync_command, ffmpeg_command, …     ← concrete commands
```

Use the engine directly when the caller is not a `system_command` subclass
(e.g. SongKong ad-hoc call, a one-off script). Use the ABC when the command
already lives in the `system_command` hierarchy — it co-locates the parser with
the command and provides a uniform `call_command_with_progress` entry point.

---

## Layer 1 — engine: `execute.execute_with_progress`

File: `lib/bes/system/execute.py`

A thin classmethod that wraps the existing `non_blocking=True` + `output_function`
machinery with a pluggable `line_parser` callable. Motivated by the recurring pattern
of tools (rsync, ffmpeg, SongKong) that emit structured progress one line at a time.

`_poll_process` in `execute.py` already handles the readline loop, stdout/stderr
separation, `\r\n` / `\r` / `\n` splitting, and `stderr_to_stdout` mode. This method
adds one layer on top: it routes each line through a caller-supplied parser, collects
the parsed events, and returns them alongside the normal `execute_result`.

### Interface

```python
execute.execute_with_progress(
  args,
  line_parser,              # callable(stdout_line, stderr_line) -> Any | None
  progress_cb=None,         # callable(event) -> None  (optional, called live)
  progress_source='both',   # 'stdout' | 'stderr' | 'both'
  **kwargs                  # forwarded verbatim to execute.execute()
) -> execute_progress_result
```

#### `line_parser`

Called once per readline tick when the tick carries output from the selected
`progress_source` stream. Both arguments are always passed; the parser decides
which to read.

- Return a value (any type) to record it as an event.
- Return `None` to silently skip (no event recorded, no callback fired).

The parser is the caller's responsibility. `execute_with_progress` does not
interpret the return value.

#### `progress_source`

Filters which readline ticks trigger the parser:

| value | behaviour |
|---|---|
| `'stdout'` | call parser only when `stdout_line` is non-empty |
| `'stderr'` | call parser only when `stderr_line` is non-empty |
| `'both'` | call parser whenever either stream has output (default) |

rsync emits progress on stderr → use `'stderr'`.
ffmpeg emits progress on stderr → use `'stderr'`.
SongKong emits progress on stdout → use `'stdout'`.
Default `'both'` preserves backward compatibility.

#### `progress_cb`

Optional. Called immediately (live, during execution) for each non-`None` event.
If omitted, events are still collected and available in the result.

#### `**kwargs`

All keyword arguments forwarded to `execute.execute()`. `non_blocking=True` is
set internally and must not be passed by the caller (raises `ValueError`). All
other options (`cwd`, `env`, `stderr_to_stdout`, `raise_error`, etc.) are available.

#### Return value: `execute_progress_result`

```python
execute_progress_result(result, events)
```

- **`result`** — the underlying `execute_result` (stdout, stderr, exit_code, command).
- **`events`** — list of all non-`None` values returned by `line_parser`, in order.

### Implementation

```python
_execute_progress_result = namedtuple('_execute_progress_result', 'result, events')

@classmethod
def execute_with_progress(clazz, args, line_parser, progress_cb=None,
                          progress_source='both', **kwargs):
  check.check_callable(line_parser)
  check.check_callable(progress_cb, allow_none=True)
  check.check_string(progress_source)
  if 'non_blocking' in kwargs:
    raise ValueError('non_blocking is set internally by execute_with_progress')
  if progress_source not in ('stdout', 'stderr', 'both'):
    raise ValueError(f'progress_source must be stdout, stderr, or both: "{progress_source}"')

  events = []
  def _output_function(output):
    if progress_source == 'stdout' and not output.stdout:
      return
    if progress_source == 'stderr' and not output.stderr:
      return
    event = line_parser(output.stdout, output.stderr)
    if event is not None:
      events.append(event)
      if progress_cb:
        progress_cb(event)

  result = clazz.execute(args, non_blocking=True, output_function=_output_function, **kwargs)
  return _execute_progress_result(result, events)
```

### Ad-hoc usage example (SongKong — no ABC)

SongKong is not a `system_command` subclass. Call the engine directly:

```python
from bes.system.execute import execute
from rmusic.songkong.rmusic_songkong_progress import rmusic_songkong_progress

def _on_event(event):
  if event.kind == 'progress':
    print(f'  {event.counts}')

rv = execute.execute_with_progress(
  ['/Applications/SongKong.app/Contents/MacOS/SongKong', '-m', album_dir],
  line_parser=rmusic_songkong_progress.parse_line,
  progress_cb=_on_event,
  progress_source='stdout',
  env={'HOME': tmp_home},
  raise_error=False,
)
summary = {e.key: e.value for e in rv.events if e.kind == 'summary'}
```

---

## Layer 2 — ABC: `system_command_with_progress`

File: `lib/bes/system/system_command_with_progress.py`

An abstract base class in the `system_command` hierarchy. Commands that emit
parseable progress inherit from it, implement two abstract classmethods, and
get `call_command_with_progress` for free.

### Class hierarchy

```
system_command  (ABC — lib/bes/system/system_command.py)          unchanged
    └── system_command_with_progress  (ABC — lib/bes/system/system_command_with_progress.py)  NEW
            ├── bf_rsync_command   (lib/bes/files/rsync/bf_rsync_command.py)
            └── ffmpeg_command     (bav — migrate later, out of scope now)
```

Commands that do not need progress keep `system_command` as their base.

### Abstract interface

```python
@classmethod
@abstractmethod
def progress_source(clazz):
  'Which stream carries progress: "stdout", "stderr", or "both".'

@classmethod
@abstractmethod
def parse_progress_line(clazz, stdout_line, stderr_line):
  '''Parse one readline tick.

  Return a non-None value to emit it as an event; return None to skip.
  '''
```

### Concrete classmethod: `call_command_with_progress`

Mirrors `call_command` from `system_command`: resolves the executable, prepends
`static_args`, delegates to the engine. Returns `execute_result`; the events list
is discarded because callers use `progress_cb` for live updates. Raises
`clazz.error_class()` on non-zero exit.

### Full implementation

```python
from abc import abstractmethod

from bes.system.execute import execute
from bes.system.system_command import system_command

class system_command_with_progress(system_command):
  'system_command subclass for commands that emit parseable progress output.'

  @classmethod
  @abstractmethod
  def progress_source(clazz):
    'Which stream carries progress lines: "stdout", "stderr", or "both".'
    raise NotImplementedError('progress_source')

  @classmethod
  @abstractmethod
  def parse_progress_line(clazz, stdout_line, stderr_line):
    raise NotImplementedError('parse_progress_line')

  @classmethod
  def call_command_with_progress(clazz, args, progress_cb=None, quote=True, **kwargs):
    exe = clazz._find_exe()
    static = clazz.static_args() or []
    cmd = [exe] + list(static) + list(args)
    progress_result = execute.execute_with_progress(
      cmd,
      line_parser=clazz.parse_progress_line,
      progress_cb=progress_cb,
      progress_source=clazz.progress_source(),
      raise_error=False,
      quote=quote,
      **kwargs,
    )
    if progress_result.result.exit_code != 0:
      raise clazz.error_class()(
        f'{clazz.exe_name()} failed: {progress_result.result.stderr}'
      )
    return progress_result.result
```

---

## Concrete example: `bf_rsync_command`

File: `lib/bes/files/rsync/bf_rsync_command.py`

### rsync progress output format

rsync writes per-file transfer progress to **stderr** using `\r` for in-place
terminal updates:

```
          0   0%    0.00kB/s    0:00:00
    163,577,856  93%  110.33MB/s    0:00:01
    175,792,128 100%  110.74MB/s    0:00:01 (xfr#1, to-chk=0/1)
```

Pattern: `^\s*([\d,]+)\s+(\d+)%\s+(\S+)\s+(\d+:\d+:\d+)`

Fields: `bytes_done`, `percent`, `rate`, `elapsed`. The trailing `(xfr#…)` is
optional and ignored.

### Implementation

Change base class from `system_command` to `execute_with_progress`. Add the
`rsync_progress` namedtuple and the two abstract implementations:

```python
import re
from collections import namedtuple

from bes.system.system_command_with_progress import system_command_with_progress

from .bf_rsync_error import bf_rsync_error

rsync_progress = namedtuple('rsync_progress', 'bytes_done, percent, rate, elapsed')

_PROGRESS_RE = re.compile(r'^\s*([\d,]+)\s+(\d+)%\s+(\S+)\s+(\d+:\d+:\d+)')

class bf_rsync_command(system_command_with_progress):

  @classmethod
  def exe_name(clazz): return 'rsync'

  @classmethod
  def extra_path(clazz): return None

  @classmethod
  def error_class(clazz): return bf_rsync_error

  @classmethod
  def static_args(clazz): return None

  @classmethod
  def supported_systems(clazz): return ('linux', 'macos')

  @classmethod
  def progress_source(clazz): return 'stderr'

  @classmethod
  def parse_progress_line(clazz, stdout_line, stderr_line):
    match = _PROGRESS_RE.match(stderr_line or '')
    if not match:
      return None
    return rsync_progress(
      bytes_done=int(match.group(1).replace(',', '')),
      percent=int(match.group(2)),
      rate=match.group(3),
      elapsed=match.group(4),
    )
```

`call_command` (no progress) is inherited from `system_command` unchanged and
remains the entry point for all SSH helper calls in `bf_rsync_file_sync`.

---

## Wiring: `bf_rsync_file_sync`

File: `lib/bes/files/rsync/bf_rsync_file_sync.py`

### `_rsync` — add `--progress`, switch to `call_command_with_progress`

The existing method uses `_rsync_ssh_command()` to build the `-e` string; keep
that helper, only change the rsync arg list and the call site:

```python
def _rsync(self, src, dest_path):
  cmd = [
    '--partial', '--partial-dir=.rsync-partial',
    '--exclude=**/.DS_Store',
    '--human-readable', '--stats',
    '--progress',
    '--timeout=300',
    '-va',
    '-e', self._rsync_ssh_command(),
    src,
    f'{self._host}:{dest_path}',
  ]
  progress_cb = self._on_rsync_progress if self._show_progress else None
  bf_rsync_command.call_command_with_progress(cmd, progress_cb=progress_cb, quote=False)
  if self._show_progress:
    sys.stdout.write('\n')
    sys.stdout.flush()
```

### `_on_rsync_progress`

```python
def _on_rsync_progress(self, event):
  line = (f'\r  {bf_size.sizeof_fmt(event.bytes_done)}'
          f'  {event.percent}%  {event.rate}  {event.elapsed}   ')
  sys.stdout.write(line)
  sys.stdout.flush()
```

`\r` overwrites the same terminal line on every event. Trailing spaces erase
leftover characters when a shorter line follows a longer one. The `\n` written
after the call freezes the final state in the scrollback.

### TTY guard

Set in `__init__` or `_run_loop` so it is computed once per run:

```python
self._show_progress = sys.stdout.isatty()
```

When stdout is redirected (log file, pipe), progress updates are suppressed
by passing `progress_cb=None`. The file still receives the final transferred/skipped
line from the progress tracker.

### Integration with `bf_rsync_progress_tracker`

The tracker's `begin_file` currently shows `starting...` and `finish_file`
overwrites it with the final status line. With live rsync progress, `_on_rsync_progress`
will overwrite the `starting...` line on every event with byte/percent/rate, then
`finish_file` overwrites it one final time with the completed status. No changes
to the tracker interface are needed — the overwrite chain is handled by `\r` in all
three cases.

---

## Unit tests

### Engine tests — `tests/lib/bes/system/test_execute_with_progress.py`

Tests use inline Python scripts as mock subprocesses (no shell script required).
Pattern: `self.make_temp_file(content=..., perm=0o0755, suffix='.py')`.

**`test_events_collected`**
Parser returns a string event for each of 3 known lines. Assert `rv.events == ['line1', 'line2', 'line3']`.

**`test_none_filtered`**
Parser returns `None` for lines containing `'skip'`. Assert only non-skip lines appear in `rv.events`.

**`test_progress_cb_called_live`**
Append to a list inside `progress_cb`. Assert the list matches `rv.events` — confirms callback fires during execution, not after.

**`test_progress_cb_not_called_for_none`**
Parser returns `None` for every line. Assert `progress_cb` is never called and `rv.events` is empty.

**`test_result_has_execute_result`**
Assert `rv.result.exit_code == 0` and `rv.result.stdout` contains expected content — verifies `execute_result` passes through unmodified.

**`test_stderr_lines_reach_parser`**
Mock script writes to stderr. Pass `stderr_to_stdout=True`. Assert parser receives those lines and events are collected.

**`test_non_blocking_not_allowed_in_kwargs`**
Assert that passing `non_blocking=True` raises `ValueError`.

**`test_parser_receives_correct_stdout_stderr`**
Mock script writes distinct strings to stdout and stderr (without `stderr_to_stdout`). Parser records `(stdout_line, stderr_line)` tuples. Assert streams land in correct positions.

**`test_empty_output`**
Mock script prints nothing and exits 0. Assert `rv.events == []` and `rv.result.exit_code == 0`.

**`test_high_line_count`**
Mock script prints 1000 lines. Assert all 1000 events collected — sanity check that the readline loop drops nothing.

**`test_progress_source_stdout_filters_stderr`**
Mock script writes to both streams. `progress_source='stdout'`. Assert parser is not called for stderr-only ticks, only stdout ticks produce events.

**`test_progress_source_stderr_filters_stdout`**
Inverse of above: `progress_source='stderr'`. Assert only stderr ticks produce events.

**`test_progress_source_invalid_raises`**
Assert that `progress_source='bad'` raises `ValueError`.

### `bf_rsync_command` parser tests — `tests/lib/bes/files/rsync/test_bf_rsync_command.py`

**`test_parse_progress_line_full`**
Pass a well-formed rsync progress line as `stderr_line`. Assert returned `rsync_progress` has correct `bytes_done`, `percent`, `rate`, `elapsed`.

**`test_parse_progress_line_with_comma_bytes`**
`'  1,048,576  50%  10.00MB/s  0:00:05'` → `bytes_done == 1048576`.

**`test_parse_progress_line_none_for_non_progress`**
Pass an rsync stats line (`'total size is …'`) and a blank line. Assert `None` returned for both.

**`test_parse_progress_line_final_with_xfr_suffix`**
`'  175,792,128 100%  110.74MB/s  0:00:01 (xfr#1, to-chk=0/1)'` → valid event, `percent == 100`.

---

## What does NOT change

- `system_command.call_command` — unchanged, still the entry point for all SSH helpers
  (`_ssh_sha256`, `_ssh_mkdir`, `_ssh_mv`, `_cleanup_partial`).
- `execute_result` type — unchanged.
- Dry-run path in `bf_rsync_file_sync` — never calls `_rsync`, so progress is never shown.
- `ffmpeg_command` / `ffmpeg_transcode._run_with_progress` in `bav` — unchanged for now;
  migrate to `system_command_with_progress` ABC in a separate session when ffmpeg work resumes.
- The retry loop, `_run_loop`, and `bf_rsync_progress_tracker` — no structural changes.

---

## Files changed

| file | change |
|---|---|
| `lib/bes/system/execute.py` | add `_execute_progress_result` namedtuple; add `execute_with_progress` classmethod with `progress_source` parameter |
| `lib/bes/system/system_command_with_progress.py` | **new** — ABC with `progress_source`, `parse_progress_line`, `call_command_with_progress` |
| `lib/bes/files/rsync/bf_rsync_command.py` | change base to `system_command_with_progress`; add `rsync_progress` namedtuple, `progress_source`, `parse_progress_line` |
| `lib/bes/files/rsync/bf_rsync_file_sync.py` | update `_rsync` to use `call_command_with_progress`; add `_on_rsync_progress`; add `_show_progress` TTY guard |
| `tests/lib/bes/system/test_execute_with_progress.py` | **new** — 13 engine tests |
| `tests/lib/bes/files/rsync/test_bf_rsync_command.py` | add 4 parser tests |
