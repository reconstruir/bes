# execute_with_progress — rsync progress proposal

> **Status**: shelved pending reconciliation with `execute-with-progress.md` from a prior session.
> Do not implement until both documents are reviewed together.

---

## Context

This proposal grew out of adding live rsync transfer progress to `bf_rsync_file_sync`.
It reuses `execute.execute_with_progress` (already implemented in `lib/bes/system/execute.py`)
and introduces a new abstract class `execute_with_progress` that slots into the
`system_command` hierarchy so individual commands can declare how to parse their own
progress output without duplicating subprocess machinery.

### What `execute.execute_with_progress` already provides

- Two threads reading stdout and stderr concurrently (no deadlock on full pipes)
- Splits on `\r\n`, `\r`, or `\n` (handles tools that use `\r` for in-place updates)
- `line_parser(stdout_line, stderr_line)` callback per line
- `progress_cb(event)` called live for every non-None event
- `progress_source` selects which stream triggers the parser (`'stdout'`, `'stderr'`, `'both'`)
- Returns `_execute_progress_result(result, events)`

### What rsync outputs with `--progress`

rsync writes progress to **stderr**, using `\r` for in-place terminal updates:

```
          0   0%    0.00kB/s    0:00:00
    163,577,856  93%  110.33MB/s    0:00:01
    175,792,128 100%  110.74MB/s    0:00:01 (xfr#1, to-chk=0/1)
```

Pattern: `^\s*([0-9,]+)\s+(\d+)%\s+(\S+)\s+(\S+)`

Fields: `bytes_done`, `percent`, `rate`, `elapsed` (the trailing `(xfr#…)` is optional and ignored).

---

## Class hierarchy

```
system_command  (ABC — lib/bes/system/system_command.py)
    └── execute_with_progress  (ABC — lib/bes/system/execute_with_progress.py)  ← NEW
            ├── bf_rsync_command   (lib/bes/files/rsync/bf_rsync_command.py)    ← change base
            └── ffmpeg_command     (bav — could migrate later, not in this scope)
```

`system_command` is unchanged. `execute_with_progress` extends it, adding two abstract
classmethods and one concrete classmethod. Commands that do not need progress keep
`system_command` as their base.

---

## New file: `lib/bes/system/execute_with_progress.py`

```python
from abc import abstractmethod

from bes.system.execute import execute
from bes.system.system_command import system_command

class execute_with_progress(system_command):
  'system_command subclass for commands that emit parseable progress output.'

  @classmethod
  @abstractmethod
  def progress_source(clazz):
    'Which stream carries progress lines: "stdout", "stderr", or "both".'
    raise NotImplementedError('progress_source')

  @classmethod
  @abstractmethod
  def parse_progress_line(clazz, stdout_line, stderr_line):
    '''Parse one line from the progress stream.

    stdout_line is the line string when it came from stdout, else None.
    stderr_line is the line string when it came from stderr, else None.

    Return a non-None value to emit it as a progress event; return None to skip.
    '''
    raise NotImplementedError('parse_progress_line')

  @classmethod
  def call_command_with_progress(clazz, args, progress_cb=None, quote=True, **kwargs):
    '''Run the command, parsing progress lines live.

    Resolves the executable and prepends static_args exactly like call_command.
    Delegates to execute.execute_with_progress for the subprocess loop.
    Returns execute_result (the events list is discarded; callers use progress_cb).
    Raises clazz.error_class() on non-zero exit.
    '''
    exe = clazz._find_exe()
    static_args = clazz.static_args() or []
    cmd = [exe] + list(static_args) + list(args)
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

## Changes to `bf_rsync_command`

File: `lib/bes/files/rsync/bf_rsync_command.py`

- Change base class from `system_command` to `execute_with_progress`
- Add import for `execute_with_progress`
- Implement `progress_source` and `parse_progress_line`
- Add `rsync_progress` namedtuple for progress events

```python
import re
from collections import namedtuple

from bes.system.execute_with_progress import execute_with_progress

from .bf_rsync_error import bf_rsync_error

rsync_progress = namedtuple('rsync_progress', 'bytes_done, percent, rate, elapsed')

_PROGRESS_RE = re.compile(
  r'^\s*([\d,]+)\s+(\d+)%\s+(\S+)\s+(\d+:\d+:\d+)'
)

class bf_rsync_command(execute_with_progress):

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
    line = stderr_line or ''
    match = _PROGRESS_RE.match(line)
    if not match:
      return None
    bytes_done = int(match.group(1).replace(',', ''))
    percent = int(match.group(2))
    rate = match.group(3)
    elapsed = match.group(4)
    return rsync_progress(bytes_done, percent, rate, elapsed)
```

---

## Changes to `bf_rsync_file_sync`

File: `lib/bes/files/rsync/bf_rsync_file_sync.py`

### `_rsync` — add `--progress` and use `call_command_with_progress`

```python
def _rsync(self, src, dest_path):
  ssh_cmd = f'ssh -i {self._ssh_key}'
  if self._ssh_port is not None:
    ssh_cmd += f' -p {self._ssh_port}'
  if not self._strict_host_checking:
    ssh_cmd += ' -o StrictHostKeyChecking=no'
  if self._known_hosts_file:
    ssh_cmd += f' -o UserKnownHostsFile={self._known_hosts_file}'
  cmd = [
    '--partial', '--partial-dir=.rsync-partial',
    '--exclude=**/.DS_Store',
    '--human-readable', '--stats',
    '--progress',          # ← added
    '-va',
    '-e', ssh_cmd,
    src,
    f'{self._host}:{dest_path}',
  ]
  self._progress_bytes = 0
  bf_rsync_command.call_command_with_progress(
    cmd,
    progress_cb=self._on_rsync_progress,
    quote=False,
  )
  sys.stdout.write('\n')
  sys.stdout.flush()
```

### New `_on_rsync_progress`

```python
def _on_rsync_progress(self, event):
  line = f'\r  {bf_size.sizeof_fmt(event.bytes_done)}  {event.percent}%  {event.rate}  {event.elapsed}   '
  sys.stdout.write(line)
  sys.stdout.flush()
```

The `\r` keeps overwriting the same terminal line. The trailing spaces erase leftover
characters if a shorter line follows a longer one. The `\n` printed after
`call_command_with_progress` returns freezes the final progress state in the log.

### TTY guard (recommended follow-on)

Progress line-overwriting only makes sense on a real terminal. Add a guard so that
when stdout is redirected to a file the progress updates are suppressed:

```python
import sys

self._show_progress = sys.stdout.isatty()
```

Use `self._show_progress` in `_rsync` to decide whether to pass `progress_cb` or `None`.

### `sys` import

Add `import sys` to `bf_rsync_file_sync.py` imports (it is not currently imported).

---

## What does NOT change

- `call_command` (no progress) remains on `system_command` and is used for all SSH
  calls (`_ssh_sha256`, `_ssh_mkdir`, `_cleanup_partial`) — none of those need progress.
- Dry-run path never calls `_rsync`, so progress is never shown for dry runs.
- The timestamped `[TRANSFER]` log line from `_emit` is still printed before rsync
  starts; progress updates follow it on subsequent lines with `\r` in-place refresh.
- `ffmpeg_command` / `ffmpeg_transcode._run_with_progress` are unchanged for now.

---

## Reconciliation notes for later

The prior `execute-with-progress.md` documents `execute_with_progress` as a plain
classmethod added directly to `execute`, driven by a caller-supplied `line_parser`
callable — no class hierarchy, no abstract methods.

This document proposes an **abstract base class** in the `system_command` hierarchy,
where each command owns its parser as a classmethod. The two approaches are
complementary:

- The `execute.execute_with_progress` method (already implemented) is the low-level
  engine that both approaches use.
- The abstract class proposed here is a higher-level convention that ties progress
  parsing to a specific command, avoiding anonymous lambdas scattered at call sites.

When reconciling, decide whether the abstract class is worth the extra file and
inheritance depth, or whether the simpler caller-supplies-parser approach from the
prior doc is sufficient.
