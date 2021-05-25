#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from bes.common.check import check
from bes.fs.file_util import file_util
from bes.fs.file_check import file_check
from bes.python.python_version import python_version
from bes.script.blurber import blurber

from .pyinstaller_build import pyinstaller_build
from .pyinstaller_options import pyinstaller_options

class pyinstaller_cli_handler(cli_command_handler):
  'PyInstaller cli handler.'

  def __init__(self, cli_args):
    super(pyinstaller_cli_handler, self).__init__(cli_args, options_class = pyinstaller_options)
    check.check_pyinstaller_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)

  def build(self, script_filename, output_filename):
    file_check.check_file(script_filename)
    check.check_string(output_filename)

  def build(clazz, script_filename,
            python_path = None,
            log_level = None,
            excludes = None,
            hidden_imports = None,
            verbose = False,
            cwd = None,
            replace_env = None,
            exe = None):
    
    
    return 0
