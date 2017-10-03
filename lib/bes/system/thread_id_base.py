#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class thread_id_base(with_metaclass(ABCMeta, object)):
  
  def __init__(self):
    pass
  
  @abstractmethod
  def thread_id(self):
    'Return the current thread id.'
    pass
