#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
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
from .bf_media_resolve_task import bf_media_resolve_task
from .bf_media_scan_status import bf_media_scan_status
from .bf_media_scan_task import bf_media_scan_task
from .bf_media_sort_type import bf_media_sort_type

class bf_media_finder(object):

  _log = logger('bf_media_finder')

  def __init__(self, processor):
    check.check_btask_processor(processor)

    self._processor = processor
    self._runner = btask_main_thread_runner_py()
    self._collector = btask_result_collector_py(processor, self._runner)
    self._state = bf_media_finder_state.IDLE
    self._lock = threading.Lock()
    self._scan_task_id = None
    self._resolve_task_ids = set()
    self._resolve_task_id_to_count = {}
    self._resolve_done_count = 0
    self._resolve_total_count = 0
    self._filename_index = {}
    self._entries = []
    self._callbacks = None
    self._options = None
    self._cancel_requested = False
    self._current_gen = 0

  @property
  def state(self):
    return self._state

  @property
  def entries(self):
    with self._lock:
      return list(self._entries)

  def scan(self, root_dirs, options=None, callbacks=None):
    if isinstance(root_dirs, str):
      root_dirs = [ root_dirs ]
    root_dirs = list(root_dirs)
    options = check.check_bf_media_finder_options(options, allow_none=True) or bf_media_finder_options()
    if callbacks is not None and not isinstance(callbacks, bf_media_finder_callbacks):
      raise TypeError(f'callbacks must be bf_media_finder_callbacks or None')

    with self._lock:
      old_scan_id = self._scan_task_id
      old_resolve_ids = set(self._resolve_task_ids)
      self._current_gen += 1
      gen = self._current_gen
      self._cancel_requested = False
      self._scan_task_id = None
      self._resolve_task_ids = set()
      self._resolve_task_id_to_count = {}
      self._entries = []
      self._callbacks = callbacks
      self._options = options

    # Cancel old tasks in daemon threads to avoid re-entrant lock deadlock
    for task_id in ([old_scan_id] if old_scan_id else []) + list(old_resolve_ids):
      threading.Thread(target=self._processor.cancel, args=(task_id,), daemon=True).start()

    self._transition(bf_media_finder_state.SCANNING)
    self._collector.start()

    config = btask_config('scan', limit=options.num_scan_workers)

    def _done_cb(result):
      self._on_scan_task_done(result, gen)

    def _status_cb(task_id, status):
      self._on_scan_task_status(task_id, status, gen)

    task_id = self._processor.add_task(
      bf_media_scan_task,
      callback=_done_cb,
      status_callback=_status_cb,
      config=config,
      args={
        'root_dirs':       root_dirs,
        'media_types':     options.media_types,
        'ignore_filename': options.ignore_file or None,
        'chunk_size':      options.scan_chunk_size,
      },
    )
    with self._lock:
      self._scan_task_id = task_id

  def cancel(self):
    with self._lock:
      scan_task_id = self._scan_task_id
      self._scan_task_id = None
      resolve_task_ids = set(self._resolve_task_ids)
      self._cancel_requested = True

    for task_id in ([scan_task_id] if scan_task_id else []) + list(resolve_task_ids):
      # Defer each cancel to a daemon thread: processor.cancel() acquires processor._lock,
      # which may already be held if cancel() is called from a status/done callback.
      threading.Thread(target=self._processor.cancel, args=(task_id,), daemon=True).start()

  def run(self):
    'Block until the current scan (and resolve, if triggered) completes or is cancelled.'
    self._runner.main_loop_start()
    self._collector.stop()

  # ---------------------------------------------------------------------------
  # Internal — scan phase
  # ---------------------------------------------------------------------------

  def _on_scan_task_status(self, task_id, status, gen):
    if not isinstance(status, bf_media_scan_status):
      return
    with self._lock:
      if gen != self._current_gen:
        return
      self._entries.extend(status.entries)
    cbs = self._callbacks
    if cbs and cbs.on_scan_progress:
      cbs.on_scan_progress(status.found, status.scanned)

  def _on_scan_task_done(self, result, gen):
    with self._lock:
      if gen != self._current_gen:
        return
      self._scan_task_id = None
      entries = list(self._entries)
      options = self._options
      callbacks = self._callbacks
      cancel_requested = self._cancel_requested

    if result.state == btask_result_state.CANCELLED:
      self._entries = []
      self._transition(bf_media_finder_state.IDLE)
      if cancel_requested and callbacks and callbacks.on_cancel:
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

    # Apply intrinsic sort if applicable (extended sort deferred to resolve phase)
    if isinstance(options.sort_type, bf_media_sort_type):
      if options.sort_type != bf_media_sort_type.FOUND_ORDER:
        entries = _sort_entries(entries, options.sort_type, options.case_sensitive, options.sort_reversed)
      elif options.sort_reversed:
        entries = list(reversed(entries))

    with self._lock:
      self._entries = entries

    self._transition(bf_media_finder_state.READY_QUICK)
    if callbacks and callbacks.on_scan_done:
      callbacks.on_scan_done(entries)

    # Decide whether to start the resolve phase
    if isinstance(options.sort_type, str):
      if options.attr_resolver is None:
        exc = ValueError(
          f'sort_type "{options.sort_type}" requires attr_resolver to be set in options'
        )
        self._entries = []
        self._transition(bf_media_finder_state.IDLE)
        if callbacks and callbacks.on_error:
          callbacks.on_error(exc)
        self._runner.main_loop_stop()
        return
      self._start_resolve_phase(entries, options, callbacks, gen)
    else:
      # Intrinsic sort — READY_QUICK is terminal
      self._runner.main_loop_stop()

  # ---------------------------------------------------------------------------
  # Internal — resolve phase
  # ---------------------------------------------------------------------------

  def _start_resolve_phase(self, entries, options, callbacks, gen):
    if not entries:
      self._transition(bf_media_finder_state.READY)
      if callbacks and callbacks.on_resolve_done:
        callbacks.on_resolve_done()
      self._runner.main_loop_stop()
      return

    chunk_size = options.resolve_chunk_size
    attr_name  = options.sort_type   # a string (extended sort key)
    resolver   = options.attr_resolver

    chunks = [ entries[i:i+chunk_size] for i in range(0, len(entries), chunk_size) ]

    with self._lock:
      self._resolve_done_count  = 0
      self._resolve_total_count = len(entries)
      self._filename_index = { e.filename: e for e in entries }

    self._transition(bf_media_finder_state.RESOLVING)

    config = btask_config('resolve', limit=options.num_resolve_workers)

    for chunk in chunks:
      chunk_file_count = len(chunk)
      entry_dicts = [ {'filename': e.filename, 'mime_type': e.mime_type} for e in chunk ]

      def _resolve_done_cb(result, _cfc=chunk_file_count):
        self._on_resolve_task_done(result, _cfc, gen)

      task_id = self._processor.add_task(
        bf_media_resolve_task,
        callback=_resolve_done_cb,
        config=config,
        args={
          'entries':   entry_dicts,
          'attr_name': attr_name,
          'resolver':  resolver,
        },
      )
      with self._lock:
        self._resolve_task_ids.add(task_id)

  def _on_resolve_task_done(self, result, chunk_file_count, gen):
    with self._lock:
      if gen != self._current_gen:
        return  # stale callback from a superseded scan — discard
      self._resolve_task_ids.discard(result.task_id)
      all_done        = len(self._resolve_task_ids) == 0
      cancel_requested = self._cancel_requested
      callbacks       = self._callbacks
      options         = self._options

    if cancel_requested:
      if all_done:
        self._entries = []
        self._transition(bf_media_finder_state.IDLE)
        if callbacks and callbacks.on_cancel:
          callbacks.on_cancel()
        self._runner.main_loop_stop()
      return

    if result.state == btask_result_state.SUCCESS and result.data:
      results = result.data.get('results', [])
      with self._lock:
        for item in results:
          entry = self._filename_index.get(item['filename'])
          if entry is not None:
            entry.resolved_attrs[item['attr_name']] = item['value']

    with self._lock:
      self._resolve_done_count += chunk_file_count
      done  = self._resolve_done_count
      total = self._resolve_total_count

    if callbacks and callbacks.on_resolve_progress:
      callbacks.on_resolve_progress(done, total)

    if all_done:
      resolver = options.attr_resolver
      sort_attr = options.sort_type

      def key(e):
        val = e.resolved_attrs.get(sort_attr)
        return (resolver.attr_sort_key(val), path.basename(e.filename).lower(), path.dirname(e.filename).lower())

      with self._lock:
        entries = sorted(self._entries, key=key, reverse=options.sort_reversed)
        self._entries = entries

      self._transition(bf_media_finder_state.READY)
      if callbacks and callbacks.on_resolve_done:
        callbacks.on_resolve_done()
      self._runner.main_loop_stop()

  def _transition(self, new_state):
    self._state = new_state
    self._log.log_d(f'state → {new_state.value}')
    cbs = self._callbacks
    if cbs and cbs.on_state_changed:
      cbs.on_state_changed(new_state)


def _sort_entries(entries, sort_type, case_sensitive, sort_reversed=False):
  if sort_type == bf_media_sort_type.NAME:
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
  return sorted(entries, key=key, reverse=sort_reversed)
