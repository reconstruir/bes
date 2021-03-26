#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.temp_file import temp_file

#from bes.fs.dir_util import dir_util
#from bes.fs.file_util import file_util
#from bes.system.execute import execute
#from bes.system.log import logger
#from bes.system.os_env import os_env
#from bes.url.url_util import url_util

from bes.python.python_exe import python_exe as bes_python_exe
from bes.python.python_version import python_version

from .pip_installer import pip_installer
from .pip_installer_options import pip_installer_options

class pip_installer_tester(object):
  'Pip installer tester.'

  _log = logger('pip')
  
  def __init__(self, python_exe, name, debug = False):
    bes_python_exe.check_exe(python_exe)
    check.check_string(name)

    self.python_exe = python_exe
    self.name = name
    self.tmp_dir = temp_file.make_temp_dir(suffix = '-pip-installer-tester', delete = not debug)
    options = pip_installer_options(root_dir = self.tmp_dir,
                                    python_exe = self.python_exe,
                                    verbose = debug,
                                    name = self.name)
    self.installer = pip_installer(options)
    self.python_exe_version = bes_python_exe.version(self.python_exe)
