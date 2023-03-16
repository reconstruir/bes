#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bfile_matcher_base import bfile_matcher_base
from .bfile_matcher_options import bfile_matcher_options

class bfile_matcher_metadata(bfile_matcher_base):

  def __init__(self, metadata):
    check.check_dict(metadata)

    self._metadata = metadata

  #@abstractmethod
  def match(self, entry, options):
    'Return True if entry matches.'
    check.check_bfile_entry(entry)
    check.check_bfile_matcher_options(options)

    for key, value in self._metadata.items():
      if not entry.metadata[key] == value:
        return False
    return True
