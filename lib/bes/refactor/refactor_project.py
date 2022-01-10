#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os
from os import path

from bes.common.algorithm import algorithm
from bes.fs.file_replace import file_replace
from bes.fs.file_search import file_search
from bes.system.check import check
from bes.system.log import logger

from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options

from .refactor_error import refactor_error
from .refactor_files import refactor_files

class refactor_project(object):

  _log = logger('refactor')

  _rename_item = namedtuple('_rename_item', 'src, dst')
  @classmethod
  def rename(clazz, files, src_pattern, dst_pattern,
             word_boundary = False, boundary_chars = None,
             try_git = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(word_boundary)
    check.check_set(boundary_chars, allow_none = True)
    check.check_bool(try_git)

    clazz._log.log_method_d()

    refactor_files.rename_files(files, src_pattern, dst_pattern,
                                word_boundary = word_boundary,
                                boundary_chars = boundary_chars,
                                try_git = try_git)
    clazz.replace_text(files,
                       src_pattern,
                       dst_pattern,
                       word_boundary = word_boundary,
                       boundary_chars = boundary_chars)

  @classmethod
  def replace_text(clazz, files, src_pattern, dst_pattern,
                   word_boundary = False, boundary_chars = None):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(word_boundary)
    check.check_set(boundary_chars, allow_none = True)

    clazz._log.log_method_d()

    text_files = refactor_files.resolve_text_files(files)
    matching_files = refactor_files.match_files(text_files,
                                                src_pattern,
                                                word_boundary = word_boundary,
                                                boundary_chars = boundary_chars)
    replacements = { src_pattern: dst_pattern }
    for filename in matching_files:
      file_replace.replace(filename,
                           replacements,
                           backup = False,
                           word_boundary = word_boundary,
                           boundary_chars = boundary_chars)

  @classmethod
  def copy(clazz, files, src_pattern, dst_pattern,
           word_boundary = False, boundary_chars = None,
           try_git = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(word_boundary)
    check.check_set(boundary_chars, allow_none = True)
    check.check_bool(try_git)

    clazz._log.log_method_d()

    copied_files = refactor_files.copy_files(files,
                                             src_pattern,
                                             dst_pattern,
                                             word_boundary = word_boundary,
                                             boundary_chars = boundary_chars,
                                             try_git = try_git)
    print('copied_files={}'.format(copied_files))
    clazz.replace_text(copied_files,
                       src_pattern,
                       dst_pattern,
                       word_boundary = word_boundary,
                       boundary_chars = boundary_chars)
