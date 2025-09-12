#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from ..system.check import check
from ..system.log import logger

class binary_searcher(object, metaclass = ABCMeta):

  _log = logger('binary_searcher')

  @abstractmethod
  def item_at_index(self, index):
    'Return the item at the given index.'
    raise NotImplementedError('item_at_index')

  @abstractmethod
  def compare(self, item1, item2):
    'Compare 2 items and return 0 if equal, -1 if item1 < item2 and 1 if item1 > item2.'
    raise NotImplementedError('compare')

  @abstractmethod
  def low_index(self):
    'Return the lowest possible index.'
    raise NotImplementedError('low_index')

  @abstractmethod
  def high_index(self):
    'Return the highest possible index.'
    raise NotImplementedError('high_index')
  
  def search(self, target):
    lower = self.low_index()
    upper = self.high_index() + 1
    self._log.log_d(f'search: target={target} lower={lower} upper={upper}')
    while lower < upper:   # use < instead of <=
      x = lower + (upper - lower) // 2
      val = self.item_at_index(x)
      rv = self.compare(val, target)
      self._log.log_d(f'search: lower={lower} upper={upper} x={x} val={val} rv={rv}')
      if rv == 0:
        return x
      elif rv < 0:
        if lower == x:   # this two are the actual lines
          break    # you're looking for
        lower = x
      elif rv > 0:
        upper = x
    return None
