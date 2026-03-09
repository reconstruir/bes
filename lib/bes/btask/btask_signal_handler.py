#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import signal

from bes.system.check import check

def btask_install_sigint_handler(processor, grace_seconds = 3):
  '''Install a SIGINT handler for CLI apps that calls processor.stop() then exits.

  Must be called from the main thread, after the processor is created and before
  main_loop_start() (or any blocking call).  GUI apps should NOT call this —
  they handle shutdown via their own quit path (e.g. aboutToQuit).

  Workers automatically ignore SIGINT regardless of what the parent installs.
  '''
  from .btask_processor import btask_processor as _btask_processor
  check.check_instance(processor, _btask_processor)
  check.check_int(grace_seconds)

  def _handler(sig, frame):
    processor.stop(grace_seconds = grace_seconds)
    raise SystemExit(1)

  signal.signal(signal.SIGINT, _handler)
