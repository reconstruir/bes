#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check
from bes.text.word_boundary import word_boundary

from .refactor_ast import refactor_ast
from .refactor_ast_node_type import refactor_ast_node_type
from .refactor_files import refactor_files
from .refactor_options import refactor_options
from .refactor_project import refactor_project

class refactor_command_handler(bcli_command_handler):

  #@abstractmethod
  def name(self):
    return 'refactor'

  def _make_options(self, options):
    opts = refactor_options(
      verbose = options.verbose,
      debug = options.debug,
      dry_run = options.dry_run,
      word_boundary = options.word_boundary,
      try_git = options.try_git,
      unsafe = options.unsafe,
      backup = options.backup,
    )
    opts.blurber.set_verbose(options.verbose)
    opts.word_boundary_chars = word_boundary.CHARS_UNDERSCORE
    return opts

  def _command_rename(self, files, src_pattern, dst_pattern, options):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_project.rename(files, src_pattern, dst_pattern, options = self._make_options(options))
    return 0

  def _command_copy(self, files, src_pattern, dst_pattern, copy_dirs, options):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(copy_dirs)

    refactor_project.copy(files, src_pattern, dst_pattern, copy_dirs, options = self._make_options(options))
    return 0

  def _command_rename_dirs(self, dirs, src_pattern, dst_pattern, options):
    check.check_string_seq(dirs)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_files.rename_dirs(dirs, src_pattern, dst_pattern, options = self._make_options(options))
    return 0

  def _command_rename_files(self, files, src_pattern, dst_pattern, options):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_files.rename_files(files, src_pattern, dst_pattern, options = self._make_options(options))
    return 0

  def _command_replace_text(self, files, src_pattern, dst_pattern, options):
    check.check_string_seq(files)
    check.check_string(src_pattern)
    check.check_string(dst_pattern)

    refactor_project.replace_text(files, src_pattern, dst_pattern, options = self._make_options(options))
    return 0

  def _command_reindent(self, files, indent, options):
    check.check_string_seq(files)
    check.check_int(indent)

    refactor_files.reindent_files(files, indent, options.backup)
    return 0

  def _command_grep(self, files, text, node_type, options):
    check.check_string_seq(files)
    check.check_string(text)
    check.check_refactor_ast_node_type(node_type)

    items = refactor_ast.grep(files, text, node_type, options = self._make_options(options))
    for item in items:
      print(f'{item.filename}:')
      print(f'{item.line_number}: {item.snippet}')
    return 0

  def _command_function_add_arg(self, files, function_name, arg_name, options):
    check.check_string_seq(files)
    check.check_string(function_name)
    check.check_string(arg_name)

    refactor_ast.function_add_arg(files, function_name, arg_name, options = self._make_options(options))
    return 0
