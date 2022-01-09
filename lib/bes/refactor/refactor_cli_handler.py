#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.Script import Script
from bes.common.check import check
from bes.fs.file_util import file_util
from bes.fs.file_check import file_check
from bes.script.blurber import blurber
from bes.text.word_boundary import word_boundary

from .refactor_project import refactor_project
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

    refactor_project.rename(files,
                           src_pattern,
                           dst_pattern,
                           word_boundary = self.options.word_boundary,
                           boundary_chars = word_boundary.CHARS_UNDERSCORE,
                           try_git = self.options.try_git)
    return 0

  def clone(self, files, src_pattern, dst_pattern):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_project.clone(files,
                          src_pattern,
                          dst_pattern,
                          word_boundary = self.options.word_boundary,
                          boundary_chars = word_boundary.CHARS_UNDERSCORE,
                          try_git = self.options.try_git)
    return 0
  
  def rename_dirs(self, dirs, src_pattern, dst_pattern):
    check.check_string_seq(dirs)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_files.rename_dirs(dirs,
                               src_pattern,
                               dst_pattern,
                               word_boundary = self.options.word_boundary,
                               boundary_chars = word_boundary.CHARS_UNDERSCORE,
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
                                boundary_chars = word_boundary.CHARS_UNDERSCORE,
                                try_git = True)
    return 0
  
  def replace_text(self, files, src_pattern, dst_pattern):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_project.replace_text(files,
                                 src_pattern,
                                 dst_pattern,
                                 word_boundary = self.options.word_boundary,
                                 boundary_chars = word_boundary.CHARS_UNDERSCORE)
    return 0
  
