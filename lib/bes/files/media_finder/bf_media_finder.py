#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import threading

from bes.system.check import check
from bes.system.log import logger
from bes.btask.btask_config import btask_config
from bes.btask.btask_main_thread_runner_py import btask_main_thread_runner_py
from bes.btask.btask_result_collector_py import btask_result_collector_py
from bes.btask.btask_result_state import btask_result_state

from .bf_media_file_entry import bf_media_file_entry
from .bf_media_finder_callbacks import bf_media_finder_callbacks
from .bf_media_finder_options import bf_media_finder_options
from .bf_media_finder_state import bf_media_finder_state
from .bf_media_scan_status import bf_media_scan_status
from .bf_media_scan_task import bf_media_scan_task
from .bf_media_sort_type import bf_media_sort_type

class bf_media_finder(object):

  _log = logger('bf_media_finder')

  def __init__(self, processor, num_scan_workers=2):
    check.check_btask_processor(processor)
    check.check_int(num_scan_workers)

    self._processor = processor
    self._num_scan_workers = num_scan_workers
    self._runner = btask_main_thread_runner_py()
    self._collector = btask_result_collector_py(processor, self._runner)
    self._state = bf_media_finder_state.IDLE
    self._lock = threading.Lock()
    self._scan_task_id = None
    self._entries = []
    self._callbacks = None
    self._options = None

  @property
  def state(self):
    return self._state

  def scan(self, root_dirs, options=None, callbacks=None):
    if isinstance(root_dirs, str):
      root_dirs = [ root_dirs ]
    root_dirs = list(root_dirs)
    options = check.check_bf_media_finder_options(options, allow_none=True) or bf_media_finder_options()
    if callbacks is not None and not isinstance(callbacks, bf_media_finder_callbacks):
      raise TypeError(f'callbacks must be bf_media_finder_callbacks or None')

    with self._lock:
      if self._scan_task_id is not None:
        self._processor.cancel(self._scan_task_id)
        self._scan_task_id = None
      self._entries = []
      self._callbacks = callbacks
      self._options = options

    self._transition(bf_media_finder_state.SCANNING)
    self._collector.start()

    config = btask_config('scan', limit=self._num_scan_workers)
    task_id = self._processor.add_task(
      bf_media_scan_task,
      callback=self._on_task_done,
      status_callback=self._on_task_status,
      config=config,
      args={
        'root_dirs':       root_dirs,
        'media_types':     options.media_types,
        'ignore_filename': options.ignore_file or None,
        'use_ext_filter':  not options.no_ext_filter,
      },
    )
    with self._lock:
      self._scan_task_id = task_id

  def cancel(self):
    with self._lock:
      task_id = self._scan_task_id
      self._scan_task_id = None
    if task_id is not None:
      # Defer to a thread: processor.cancel() acquires processor._lock, which may
      # already be held by report_status when cancel() is called from a status callback.
      threading.Thread(target=self._processor.cancel, args=(task_id,), daemon=True).start()

  def run(self):
    'Block until the current scan (and any cancel) completes.'
    self._runner.main_loop_start()
    self._collector.stop()

  def _transition(self, new_state):
    self._state = new_state
    self._log.log_d(f'state → {new_state.value}')
    cbs = self._callbacks
    if cbs and cbs.on_state_changed:
      cbs.on_state_changed(new_state)

  def _on_task_status(self, task_id, status):
    if not isinstance(status, bf_media_scan_status):
      return
    with self._lock:
      self._entries.extend(status.entries)
    cbs = self._callbacks
    if cbs and cbs.on_scan_progress:
      cbs.on_scan_progress(status.found, status.scanned)

  def _on_task_done(self, result):
    with self._lock:
      self._scan_task_id = None
      entries = list(self._entries)
      options = self._options
      callbacks = self._callbacks

    if result.state == btask_result_state.CANCELLED:
      self._entries = []
      self._transition(bf_media_finder_state.IDLE)
      if callbacks and callbacks.on_cancel:
        callbacks.on_cancel()
      self._runner.main_loop_stop()
      return

    if result.state != btask_result_state.SUCCESS:
      self._entries = []
      self._transition(bf_media_finder_state.IDLE)
      exc = result.error or RuntimeError(f'scan failed with state {result.state}')
      if callbacks and callbacks.on_error:
        callbacks.on_error(exc)
      self._runner.main_loop_stop()
      return

    if options.sort_type != bf_media_sort_type.FOUND_ORDER:
      if options.sort_type.is_slow:
        exc = NotImplementedError(f'slow sort type not yet implemented: {options.sort_type}')
        self._entries = []
        self._transition(bf_media_finder_state.IDLE)
        if callbacks and callbacks.on_error:
          callbacks.on_error(exc)
        self._runner.main_loop_stop()
        return
      entries = _sort_entries(entries, options.sort_type, options.case_sensitive)

    self._transition(bf_media_finder_state.READY_QUICK)
    if callbacks and callbacks.on_scan_done:
      callbacks.on_scan_done(entries)
    self._runner.main_loop_stop()


def _sort_entries(entries, sort_type, case_sensitive):
  if sort_type == bf_media_sort_type.NAME:
    key = (lambda e: e.filename.lower()) if not case_sensitive else (lambda e: e.filename)
    # sort by basename then full path as tiebreak
    import os.path as path
    key = (lambda e: (path.basename(e.filename).lower(), e.filename.lower())) if not case_sensitive \
      else (lambda e: (path.basename(e.filename), e.filename))
  elif sort_type == bf_media_sort_type.PATH:
    key = (lambda e: e.filename.lower()) if not case_sensitive else (lambda e: e.filename)
  elif sort_type == bf_media_sort_type.DATE:
    key = lambda e: (e.mtime, e.filename.lower())
  elif sort_type == bf_media_sort_type.SIZE:
    key = lambda e: (e.size, e.filename.lower())
  elif sort_type == bf_media_sort_type.KIND:
    key = (lambda e: (e.mime_type.lower(), e.filename.lower())) if not case_sensitive \
      else (lambda e: (e.mime_type, e.filename))
  else:
    return entries
  return sorted(entries, key=key)
