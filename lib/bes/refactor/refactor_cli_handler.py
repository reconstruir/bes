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
from .refactor_ast import refactor_ast

class refactor_cli_handler(cli_command_handler):
  'PyInstaller cli handler.'

  def __init__(self, cli_args):
    super(refactor_cli_handler, self).__init__(cli_args, options_class = refactor_options)
    check.check_refactor_options(self.options)
    self.options.blurber.set_verbose(self.options.verbose)
    self.options.word_boundary_chars = word_boundary.CHARS_UNDERSCORE

  def rename(self, files, src_pattern, dst_pattern):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_project.rename(files, src_pattern, dst_pattern, options = self.options)
    return 0

  def copy(self, files, src_pattern, dst_pattern, copy_dirs):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(copy_dirs)

    refactor_project.copy(files, src_pattern, dst_pattern, copy_dirs, options = self.options)
    return 0

  def rename_dirs(self, dirs, src_pattern, dst_pattern):
    check.check_string_seq(dirs)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_files.rename_dirs(dirs, src_pattern, dst_pattern, options = self.options)
    return 0

  def rename_files(self, files, src_pattern, dst_pattern):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_files.rename_files(files, src_pattern, dst_pattern, options = self.options)
    return 0

  def replace_text(self, files, src_pattern, dst_pattern):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_project.replace_text(files, src_pattern, dst_pattern, options = self.options)
    return 0

  def reindent(self, files, indent):
    check.check_string_seq(files)
    check.check_int(indent)

    refactor_files.reindent_files(files, indent, self.options.backup)
    return 0

  def grep(self, files, text, node_type):
    check.check_string_seq(files)
    check.check_string(text)
    check.check_refactor_ast_node_type(node_type)

    items = refactor_ast.grep(files, text, node_type, options = self.options)
    for item in items:
      print(f'{item.filename}:')
      print(f'{item.line_number}: {item.snippet}')
    return 0
  
  def function_add_arg(self, files, function_name, arg_name):
    check.check_string_seq(files)
    check.check_string(function_name)
    check.check_string(arg_name)

    refactor_ast.function_add_arg(files, function_name, arg_name, options = self.options)
    return 0
