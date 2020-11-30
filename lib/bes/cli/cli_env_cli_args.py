# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

from bes.python.python_exe import python_exe

class cli_env_cli_args(object):

  def env_add_args(self, parser):
    pass
  
  def _command_env(self, command, *args, **kargs):
    assert command == None
    data = {
      'python_version': sys.version.replace('\n', ''),
      'python_executable': sys.executable,
      'python_frozen': getattr(sys, 'frozen', False),
      'pyinstaller_tmp_dir': getattr(sys, '_MEIPASS', ''),
      'python_exe_for_sys_version': python_exe.exe_for_sys_version(absolute = True),
    }
    for key, value in sorted(data.items()):
      print('{:>26}: {}'.format(key, value))
    return 0
