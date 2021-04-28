# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

class cli_env_cli_args(object):

  def env_add_args(self, parser):
    pass
  
  def _command_env(self, command, *args, **kargs):
    from bes.python.python_exe import python_exe
    from bes.pyinstaller.pyinstaller import pyinstaller

    assert command == None
    data = {
      'python_version': sys.version.replace('\n', ''),
      'python_executable': sys.executable,
      'python_frozen': getattr(sys, 'frozen', False),
      'pyinstaller_tmp_dir': pyinstaller.pyinstaller_temp_dir() or '',
      'python_exe_for_sys_version': python_exe.exe_for_sys_version(absolute = True),
    }
    for key, value in sorted(data.items()):
      print('{:>26}: {}'.format(key, value))
    return 0
