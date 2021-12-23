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

class refactor_rename(object):

  _log = logger('refactor')
  
  _rename_item = namedtuple('_rename_item', 'src, dst')
  @classmethod
  def rename(clazz, files, src_pattern, dst_pattern,
             word_boundary = False, underscore = False, try_git = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(word_boundary)
    check.check_bool(try_git)

    clazz._log.log_method_d()

    refactor_files.rename_files(files, src_pattern, dst_pattern,
                                word_boundary = word_boundary,
                                underscore = underscore,
                                try_git = try_git)
    clazz.replace_text(files,
                       src_pattern,
                       dst_pattern,
                       word_boundary = word_boundary,
                       underscore = underscore)

  @classmethod
  def replace_text(clazz, files, src_pattern, dst_pattern,
                   word_boundary = False, underscore = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(word_boundary)

    clazz._log.log_method_d()

    text_files = refactor_files.resolve_text_files(files)
    matching_files = clazz.match_files(text_files, src_pattern, word_boundary = word_boundary)
    replacements = { src_pattern: dst_pattern }
    for filename in matching_files:
      file_replace.replace(filename, replacements, backup = False, word_boundary = word_boundary)
      
  @classmethod
  def search_files(clazz, filenames, text, word_boundary = False, ignore_case = False):
    'Return only the text files in filesnames.'
    result = []
    for filename in filenames:
      result += file_search.search_file(filename, text, word_boundary = word_boundary, ignore_case = ignore_case)
    return result

  @classmethod
  def match_files(clazz, filenames, text, word_boundary = False, ignore_case = False):
    search_rv = clazz.search_files(filenames, text, word_boundary = word_boundary)
    return algorithm.unique([ s.filename for s in search_rv ])
