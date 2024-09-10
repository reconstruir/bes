#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.system.check import check

from ..bf_entry import bf_entry

class bf_file_matcher_item_i(object, metaclass = ABCMeta):

  @abstractmethod
  def match(self, entry, options):
    'Return True if entry matches.'
    raise NotImplemented('match')

  @abstractmethod
  def clone(self):
    'Clone the matcher item.'
    raise NotImplemented('clone')
  
check.register_class(bf_file_matcher_item_i, name = 'bf_file_matcher_item', include_seq = False)
