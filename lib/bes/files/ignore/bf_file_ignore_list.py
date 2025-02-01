#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.object_util import object_util
from bes.system.check import check

from ..bf_entry_list import bf_entry_list

from .bf_file_ignore import bf_file_ignore
  
class bf_file_ignore_list(object):

  def __init__(self, ignore_filenames):
    ignore_filenames = object_util.listify(ignore_filenames)
    self._ignorers = [ bf_file_ignore(f) for f in ignore_filenames ]
    
  def should_ignore(self, entry):
    for ignorer in self._ignorers:
      if ignorer.should_ignore(entry):
        return True
    return False

  def filter_entries(self, entries):
    check.check_bf_entry_list(entries)
    
    return [ entry for entry in entries if not self.should_ignore(entry) ]

check.register_class(bf_file_ignore_list, include_seq = False)
