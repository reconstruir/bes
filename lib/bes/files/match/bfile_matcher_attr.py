#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .bfile_matcher_sequence import bfile_matcher_sequence
from .bfile_filename_matcher_options import bfile_filename_matcher_options

class bfile_matcher_attr(bfile_matcher_sequence):

  def __init__(self, attrs, options):
    check.check_dict(attrs)
    check.check_bfile_filename_matcher_options(options)

    self._attrs = attrs
    self._options = options

  #@abstractmethod
  def match(self, entry):
    'Return True if entry matches.'
    check.check_bfile_entry(entry)

    return self._match_sequence(entry,
                                self._attrs.items(),
                                self._options.match_type,
                                self._match_function)

  @staticmethod
  def _match_function(entry, item):
    key, value = item
    return key in entry.attributes and entry.attributes[key] == value
