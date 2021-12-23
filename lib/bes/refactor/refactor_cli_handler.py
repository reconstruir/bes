#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from bes.common.check import check
from bes.fs.file_util import file_util
from bes.fs.file_check import file_check
from bes.script.blurber import blurber

from .refactor_rename import refactor_rename
from .refactor_files import refactor_files
from .refactor_options import refactor_options

class refactor_cli_handler(cli_command_handler):
  'PyInstaller cli handler.'

  def __init__(self, cli_args):
    super(refactor_cli_handler, self).__init__(cli_args, options_class = refactor_options)
    check.check_refactor_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)

  def rename(self, files, src_pattern, dst_pattern):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_rename.rename(files,
                           src_pattern,
                           dst_pattern,
                           word_boundary = self.options.word_boundary,
                           underscore = True,
                           try_git = True)
    return 0

  def rename_dirs(self, dirs, src_pattern, dst_pattern):
    check.check_string_seq(dirs)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_files.rename_dirs(dirs,
                               src_pattern,
                               dst_pattern,
                               word_boundary = self.options.word_boundary,
                               underscore = True,
                               try_git = True)
    return 0

  def rename_files(self, files, src_pattern, dst_pattern):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_files.rename_files(files,
                                src_pattern,
                                dst_pattern,
                                word_boundary = self.options.word_boundary,
                                underscore = True,
                                try_git = True)
    return 0
  
