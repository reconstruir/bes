#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.fs.file_check import file_check
from bes.fs.file_find import file_find
from bes.fs.file_match import file_match
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.file_replace import file_replace
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_search import file_search
from bes.fs.file_util import file_util
from bes.fs.filename_util import filename_util
from bes.system.check import check
from bes.system.python import python
from bes.git.git import git

from .refactor_error import refactor_error
from .refactor_files import refactor_files

class refactor_rename(object):

  @classmethod
  def rename(clazz, files, src_pattern, dst_pattern, word_boundary = False):
    check.check_string(src_pattern)
    check.check_string(dst_pattern)
    check.check_bool(word_boundary)

