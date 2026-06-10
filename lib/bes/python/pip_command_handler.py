#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check
from bes.text.text_table import text_table

from .pip_exe import pip_exe as bes_pip_exe

class pip_command_handler(bcli_command_handler):

  def name(self):
    return 'pip'

  def _command_ver(self, pip_exe, options):
    check.check_string(pip_exe)

    version = bes_pip_exe.version(pip_exe)
    print(version)
    return 0

  def _command_info(self, pip_exe, options):
    check.check_string(pip_exe)

    info = bes_pip_exe.version_info(pip_exe)
    tt = text_table(data=zip(tuple(info._fields), info))
    print(tt)
    return 0

  def _command_filename_info(self, pip_exe, options):
    check.check_string(pip_exe)

    info = bes_pip_exe.filename_info(pip_exe)
    tt = text_table(data=zip(tuple(info._fields), info))
    print(tt)
    return 0

  def _command_exe_for_python(self, python_exe, options):
    exe = bes_pip_exe.find_exe_for_python(python_exe)
    if not exe:
      print('')
      return 1
    print(exe)
    return 0
