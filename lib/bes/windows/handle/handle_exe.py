# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.command_line import command_line
from bes.system.execute import execute
from bes.system.which import which
from bes.system.log import logger

class handle_exe(object):
  'A class to deal with windows handle.exe program.'

  _log = logger('handle')

  @classmethod
  def _find_handle_exe(clazz):
    'Find the handle.exe'

    extra_path = [
      r'c:\Program Files (x86)\Microsoft Visual Studio\Installer\resources\app\layout',
      r'c:\Program Files (x86)\Microsoft Visual Studio\Installer\resources\app\ServiceHub\Services\Microsoft.Visua#lStudio.Setup.Service',
    ]
    handle_exe_name = 'handle.exe'
    exe = which.which(handle_exe_name, extra_path = extra_path)
    if exe:
      return exe
    raise handle_error('Failed to find {}'.format(handle_exe_name))

  @classmethod
  def call_handle(clazz, args, raise_error = True):
    command_line.check_args_type(args)
    check.check_bool(raise_error)

    if isinstance(args, ( list, tuple )):
      parsed_args = list(args)
    else:
      parsed_args = command_line.parse_args(args)

    handle_exe = clazz._find_handle_exe()

    cmd = [ handle_exe, '-nobanner' ] + args
    return execute.execute(cmd, raise_error = raise_error)
