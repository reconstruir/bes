#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta

class thread_id_base(object):

  __metaclass__ = ABCMeta
  
  def __init__(self):
    pass
  
  @abstractmethod
  def thread_id(self):
    'Return the current thread id.'
    pass
