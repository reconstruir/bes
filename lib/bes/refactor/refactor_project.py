#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os
from os import path

from bes.fs.file_replace import file_replace
from bes.system.check import check
from bes.system.log import logger

from .refactor_error import refactor_error
from .refactor_files import refactor_files

class refactor_project(object):

  _log = logger('refactor')

  _rename_item = namedtuple('_rename_item', 'src, dst')
  @classmethod
  def rename(clazz, files, src_pattern, dst_pattern, options = None):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_refactor_options(options, allow_none = True)

    clazz._log.log_method_d()

    refactor_files.rename_files(files, src_pattern, dst_pattern, options = options)
    clazz.replace_text(files, src_pattern, dst_pattern, options = options) 

  @classmethod
  def replace_text(clazz, files, src_pattern, dst_pattern, options = None):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_refactor_options(options, allow_none = True)

    clazz._log.log_method_d()
    options = options or refactor_options()

    text_files = refactor_files.resolve_text_files(files)
    matching_files = refactor_files.match_files(text_files, src_pattern, options = options)
    replacements = { src_pattern: dst_pattern }
    for filename in matching_files:
      file_replace.replace(filename,
                           replacements,
                           backup = False,
                           word_boundary = options.word_boundary,
                           word_boundary_chars = options.word_boundary_chars)

  @classmethod
  def copy(clazz, files, src_pattern, dst_pattern, options = None):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_refactor_options(options, allow_none = True)

    clazz._log.log_method_d()

    copied_items = refactor_files.copy_files(files, src_pattern, dst_pattern, options = options)
    copied_files = sorted([ item.dst for item in copied_items ])
    clazz.replace_text(copied_files, src_pattern, dst_pattern, options = options)
