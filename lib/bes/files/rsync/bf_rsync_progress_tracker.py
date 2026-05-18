#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import sys
import time
from datetime import datetime

from bes.common.time_util import time_util
from bes.files.bf_size import bf_size

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
    if self._compact:
      sys.stdout.write(f'\033[2K\r{index_str} {rel_path} ...')
      sys.stdout.flush()
    else:
      line = f'{index_str} {rel_path}'
      print(line, flush=True)
      if self._log_fh:
        self._log_fh.write(line + '\n')
        self._log_fh.flush()

  def finish_file(self, entry, status, file_size, is_transfer):
    if is_transfer:
      self._bytes_done += file_size
    index_str = f'[{self._current_index}/{self._total_files}]'
    done_str = bf_size.sizeof_fmt(self._bytes_done)
    total_str = bf_size.sizeof_fmt(self._total_bytes)
    eta_str = self._compute_eta()
    line = f'{index_str} {status:<10} transferred {done_str} of {total_str}  ETA {eta_str}'
    if self._compact:
      sys.stdout.write(f'\033[2K\r{line}\n')
      sys.stdout.flush()
    else:
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

  def _compute_eta(self):
    elapsed = time.time() - self._start_time
    if elapsed <= 0 or self._bytes_done <= 0:
      return '--:--'
    rate = self._bytes_done / elapsed
    remaining = max(0, self._total_bytes - self._bytes_done)
    if rate <= 0 or remaining == 0:
      return '--:--'
    return time_util.format_eta(remaining / rate)
