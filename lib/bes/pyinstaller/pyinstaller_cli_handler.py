#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from bes.common.check import check
from bes.fs.file_util import file_util
from bes.fs.filename_util import filename_util
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

    build_dir = path.abspath(self.options.build_dir)
    script_filename_abs = path.abspath(script_filename)
    output_filename_abs = path.abspath(output_filename)

    if self.options.clean:
      file_util.remove(build_dir)
      
    file_util.mkdir(build_dir)

    pyinstaller_build.build(script_filename_abs,
                            log_level = self.options.log_level,
                            excludes = self.options.excludes,
                            hidden_imports = self.options.hidden_imports,
                            verbose = self.options.verbose,
                            cwd = build_dir,
                            replace_env = None,
                            exe = None)

    output_exe = path.join(build_dir, 'dist', self._binary_basename(script_filename_abs))
    file_util.copy(output_exe, output_filename_abs)
    return 0

  @classmethod                          
  def _binary_basename(clazz, script_filename):
    return path.basename(filename_util.without_extension(script_filename))
