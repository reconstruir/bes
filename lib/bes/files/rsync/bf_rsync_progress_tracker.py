#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import sys
import time
from datetime import datetime

from bes.common.time_util import time_util
from bes.files.bf_filename import bf_filename
from bes.files.bf_size import bf_size
from bes.system.console import console

class bf_rsync_progress_tracker(object):
  'Tracks and displays per-file progress for bf_rsync_file_sync.'

  def __init__(self, entries, compact, log_fh=None):
    self._total_files = len(entries)
    self._total_bytes = sum(path.getsize(e.absolute_filename) for e in entries)
    self._compact = compact
    self._log_fh = log_fh
    self._start_time = time.time()
    self._pause_start = None
    self._bytes_done = 0
    self._current_index = 0
    self._current_entry_path = None
    self._current_dir = None

  def begin_file(self, entry):
    absolute_path = entry.absolute_filename
    if absolute_path != self._current_entry_path:
      self._current_index += 1
      self._current_entry_path = absolute_path
    rel_path = entry.relative_filename
    rel_dir = path.dirname(rel_path)
    basename = path.basename(rel_path)

    if rel_dir != self._current_dir:
      if self._current_dir is not None and self._compact:
        sys.stdout.write('\n')
        sys.stdout.flush()
      if rel_dir:
        header = f'NEXT DIR: {rel_dir}'
        print(header, flush=True)
        if self._log_fh:
          self._log_fh.write(header + '\n')
          self._log_fh.flush()
      self._current_dir = rel_dir

    index_str = f'[{self._current_index}/{self._total_files}]'
    size_str = bf_size.sizeof_fmt(path.getsize(absolute_path))

    if self._compact:
      prefix = f'{index_str} {size_str} - '
      suffix = ' starting...'
      available = console.terminal_width() - len(prefix) - len(suffix)
      display_name = self._fit_basename(basename, available)
      sys.stdout.write(f'\033[2K\r{prefix}{display_name}{suffix}')
      sys.stdout.flush()
    else:
      line = f'{index_str} {size_str} - {rel_path}'
      print(line, flush=True)
      if self._log_fh:
        self._log_fh.write(line + '\n')
        self._log_fh.flush()

  def finish_file(self, entry, status, file_size, is_transfer, reason=''):
    if is_transfer:
      self._bytes_done += file_size
    index_str = f'[{self._current_index}/{self._total_files}]'
    rel_path = entry.relative_filename
    basename = path.basename(rel_path)
    size_str = bf_size.sizeof_fmt(file_size)
    done_str = bf_size.sizeof_fmt(self._bytes_done)
    total_str = bf_size.sizeof_fmt(self._total_bytes)
    eta_str = self._compute_eta()
    accounting = f'{done_str} / {total_str}  ETA {eta_str}'

    if self._compact:
      if status in ('RENAME', 'DRY-RENAME', 'MV', 'DRY-MV') and reason:
        status_part = status
        arrow_suffix = f' → {reason}'
      elif reason:
        status_part = f'{status} - {reason}'
        arrow_suffix = None
      else:
        status_part = status
        arrow_suffix = None

      prefix = f'{index_str} {size_str} - '
      tail = f' - {status_part} - {accounting}'
      available = console.terminal_width() - len(prefix) - len(tail)

      if arrow_suffix is not None:
        avail_for_base = available - len(arrow_suffix)
        if avail_for_base > 4:
          try:
            display_name = f'{bf_filename.shorten(basename, max_length=avail_for_base)}{arrow_suffix}'
          except ValueError:
            display_name = f'{basename}{arrow_suffix}'
        else:
          display_name = f'{basename}{arrow_suffix}'
      else:
        display_name = self._fit_basename(basename, available)

      line = f'{prefix}{display_name}{tail}'
      sys.stdout.write(f'\033[2K\r{line}\n')
      sys.stdout.flush()
    else:
      if status in ('RENAME', 'DRY-RENAME', 'MV', 'DRY-MV') and reason:
        detail = f'→ {reason}  '
      elif reason:
        detail = f'{reason}  '
      else:
        detail = ''
      line = f'{index_str} {status:<10} {detail}{accounting}'
      print(line, flush=True)
      print(flush=True)

    if self._log_fh:
      ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      self._log_fh.write(f'{ts} {line}\n')
      if not self._compact:
        self._log_fh.write('\n')
      self._log_fh.flush()

  def pause_clock(self):
    self._pause_start = time.time()

  def resume_clock(self):
    if self._pause_start is not None:
      self._start_time += time.time() - self._pause_start
      self._pause_start = None

  def _fit_basename(self, basename, available):
    'Shorten basename to fit within available characters, preserving extension.'
    if available <= 0 or len(basename) <= available:
      return basename
    if available > 4:
      try:
        return bf_filename.shorten(basename, max_length=available)
      except ValueError:
        pass
    return basename

  def _compute_eta(self):
    elapsed = time.time() - self._start_time
    if elapsed <= 0 or self._bytes_done <= 0:
      return '--:--'
    rate = self._bytes_done / elapsed
    remaining = max(0, self._total_bytes - self._bytes_done)
    if rate <= 0 or remaining == 0:
      return '--:--'
    return time_util.format_eta(remaining / rate)
