#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from bes.common.object_util import object_util

from bes.files.bf_path import bf_path
from .file_ignore import file_ignore
  
class file_multi_ignore(object):

  def __init__(self, ignore_filenames):
    ignore_filenames = object_util.listify(ignore_filenames)
    self._ignorers = [ file_ignore(f) for f in ignore_filenames ]
    
  def should_ignore(self, ford):
    for ignorer in self._ignorers:
      if ignorer.should_ignore(ford):
        return True
    return False

  def filter_files(self, files):
    check.check_string_seq(files)
    check.check_string_seq(files)
    return [ f for f in files if not self.should_ignore(f) ]

check.register_class(file_multi_ignore, include_seq = False)
