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

  def begin_file(self, entry):
    absolute_path = entry.absolute_filename
    if absolute_path != self._current_entry_path:
      self._current_index += 1
      self._current_entry_path = absolute_path
    index_str = f'[{self._current_index}/{self._total_files}]'
    rel_path = entry.relative_filename
    size_str = bf_size.sizeof_fmt(path.getsize(absolute_path))

    if self._compact:
      prefix = f'{index_str} {size_str} - '
      suffix = ' ...'
      available = console.terminal_width() - len(prefix) - len(suffix)
      display_path = self._fit_path(rel_path, available)
      sys.stdout.write(f'\033[2K\r{prefix}{display_path}{suffix}')
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
    done_str = bf_size.sizeof_fmt(self._bytes_done)
    total_str = bf_size.sizeof_fmt(self._total_bytes)
    eta_str = self._compute_eta()
    accounting = f'{done_str} / {total_str}  ETA {eta_str}'

    if self._compact:
      if status in ('RENAME', 'DRY-RENAME') and reason:
        path_part = f'{rel_path} → {reason}'
      elif reason:
        path_part = f'{rel_path}  {reason}'
      else:
        path_part = rel_path
      line = f'{index_str} {status:<10} {path_part}  {accounting}'
      sys.stdout.write(f'\033[2K\r{line}\n')
      sys.stdout.flush()
    else:
      if status in ('RENAME', 'DRY-RENAME') and reason:
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

  def _fit_path(self, rel_path, available):
    'Shorten rel_path to fit within available characters, preserving the extension.'
    if available <= 0 or len(rel_path) <= available:
      return rel_path
    dirname = path.dirname(rel_path)
    basename = path.basename(rel_path)
    if dirname:
      available_for_base = available - len(dirname) - 1
      if available_for_base > 4:
        try:
          return f'{dirname}/{bf_filename.shorten(basename, max_length=available_for_base)}'
        except ValueError:
          pass
      # Directory portion alone is too long; fall back to .../{basename}
      ellipsis = '.../'
      available_for_base = available - len(ellipsis)
      if available_for_base > 4:
        try:
          return f'{ellipsis}{bf_filename.shorten(basename, max_length=available_for_base)}'
        except ValueError:
          pass
    else:
      if available > 4:
        try:
          return bf_filename.shorten(basename, max_length=available)
        except ValueError:
          pass
    return rel_path

  def _compute_eta(self):
    elapsed = time.time() - self._start_time
    if elapsed <= 0 or self._bytes_done <= 0:
      return '--:--'
    rate = self._bytes_done / elapsed
    remaining = max(0, self._total_bytes - self._bytes_done)
    if rate <= 0 or remaining == 0:
      return '--:--'
    return time_util.format_eta(remaining / rate)
