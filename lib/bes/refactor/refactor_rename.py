#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os
from os import path

from bes.common.algorithm import algorithm
from bes.fs.file_check import file_check
from bes.fs.file_find import file_find
#from bes.fs.file_match import file_match
#from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
#from bes.fs.file_replace import file_replace
#from bes.fs.file_resolver import file_resolver
#from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
#from bes.fs.filename_util import filename_util
from bes.system.check import check
#from bes.system.python import python
from bes.system.log import logger
#from bes.git.git import git
from bes.git.git import git
from bes.git.git_error import git_error
from bes.fs.file_match import file_match
from bes.fs.file_replace import file_replace

from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options

from .refactor_error import refactor_error
from .refactor_files import refactor_files

class refactor_rename(object):

  _rename_item = namedtuple('_rename_item', 'src, dst')
  _log = logger('refactor')
  @classmethod
  def rename(clazz, files, src_pattern, dst_pattern,
             word_boundary = False,
             underscore = False,
             try_git = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(word_boundary)
    check.check_bool(try_git)

    clazz._log.log_method_d()

    refactor_files.rename_files(files, src_pattern, dst_pattern,
                                word_boundary = word_boundary,
                                underscore = underscore,
                                try_git = try_git)
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
