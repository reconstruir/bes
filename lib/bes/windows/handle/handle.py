# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.which import which
from bes.system.log import logger

from .handle_exe import handle_exe
from .handle_output_parser import handle_output_parser

class handle(object):
  'A class to abstract some handle operations.'

  _log = logger('handle')

  @classmethod
  def open_handles(clazz, pid):
    check.check_int(pid)

    args = [ '-p', str(pid) ]
    rv = handle_exe.call_handle(args)
    return handle_output_parser.parse_handle_output(rv.stdout)
