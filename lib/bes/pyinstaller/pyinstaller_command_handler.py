#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.files.bf_check import bf_check
from bes.files.bf_file_ops import bf_file_ops
from bes.system.check import check

from .pyinstaller_build import pyinstaller_build
from .pyinstaller_options import pyinstaller_options

class pyinstaller_command_handler(bcli_command_handler):

  def name(self):
    return 'pyinstaller'

  def _command_build(self, script_filename, output_filename, build_dir, clean, windowed,
                     osx_bundle_identifier, excludes, hidden_imports, log_level,
                     python_version, options):
    bf_check.check_file(script_filename)
    check.check_string(output_filename)

    script_filename_abs = path.abspath(script_filename)
    output_filename_abs = path.abspath(output_filename)

    opts = pyinstaller_options(verbose=options.verbose,
                               debug=options.debug,
                               build_dir=build_dir,
                               clean=clean,
                               windowed=windowed,
                               osx_bundle_identifier=osx_bundle_identifier,
                               excludes=excludes,
                               hidden_imports=hidden_imports,
                               log_level=log_level,
                               python_version=python_version)
    result = pyinstaller_build.build(script_filename_abs, options=opts)
    bf_file_ops.copy(result.output_exe, output_filename_abs)
    return 0
