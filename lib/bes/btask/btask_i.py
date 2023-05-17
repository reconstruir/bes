#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.system.check import check

class btask_i(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def category(self):
    'Return category for this type of task'
    raise NotImplemented('category')

  @abstractmethod
  def priority(self):
    'Return  priority for this type of task'
    raise NotImplemented('priority')

  @abstractmethod
  def run(self, *args, **kargs):
    raise NotImplemented('run')

  @abstractmethod
  def callback(self, result):
    raise NotImplemented('callback')
