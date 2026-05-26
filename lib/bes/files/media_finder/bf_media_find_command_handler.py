#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import signal
import sys
import time

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.btask.btask_processor import btask_processor
from bes.system.check import check

from .bf_media_find_cli_options import bf_media_find_cli_options
from .bf_media_finder import bf_media_finder
from .bf_media_finder_callbacks import bf_media_finder_callbacks
from .bf_media_finder_state import bf_media_finder_state

class bf_media_find_command_handler(bcli_command_handler):

  #@abstractmethod
  def name(self):
    return 'bf_media_find'

  def _command_find(self, where, options):
    check.check_string_seq(where)
    check.check_bf_media_find_cli_options(options)

    processor = btask_processor('media_find', num_processes=4)
    finder = bf_media_finder(processor)

    all_entries = []
    start = time.monotonic()

    def _progress(found, scanned):
      sys.stderr.write(f'\r  scanning:  found {found:,}  scanned {scanned:,}    ')
      sys.stderr.flush()
      if options.verbose:
        pass  # verbose filenames printed in on_scan_done in found_order

    def _done(entries):
      all_entries.extend(entries)
      if options.verbose:
        for entry in entries:
          print(entry.filename)

    def _resolve_progress(done, total):
      sys.stderr.write(f'\r  resolving: {done:,}/{total:,}    ')
      sys.stderr.flush()

    def _resolve_done():
      pass  # final line cleared by the summary write below

    def _cancel():
      pass  # main_loop_stop already called; we detect via state below

    def _error(exc):
      sys.stderr.write(f'\nerror: {exc}\n')

    cbs = bf_media_finder_callbacks(
      on_scan_progress    = _progress,
      on_scan_done        = _done,
      on_resolve_progress = _resolve_progress,
      on_resolve_done     = _resolve_done,
      on_cancel           = _cancel,
      on_error            = _error,
    )

    original_sigint = signal.getsignal(signal.SIGINT)

    def _sigint(sig, frame):
      signal.signal(signal.SIGINT, original_sigint)
      finder.cancel()

    signal.signal(signal.SIGINT, _sigint)

    finder.scan(where, options=options.finder_options, callbacks=cbs)
    finder.run()  # blocks until done or cancelled

    signal.signal(signal.SIGINT, original_sigint)

    elapsed = time.monotonic() - start

    if finder.state == bf_media_finder_state.IDLE:
      sys.stderr.write('\ncancelled\n')
      processor.stop()
      return 1

    sys.stderr.write(f'\r  done: {len(all_entries):,} files in {elapsed:.1f}s\n')

    if not options.verbose and not options.count:
      for entry in all_entries:
        print(entry.filename)
    elif options.count:
      print(len(all_entries))

    processor.stop()
    return 0
