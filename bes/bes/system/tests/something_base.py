#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from abc import abstractmethod, ABCMeta

class something_base(object):

  __metaclass__ = ABCMeta
  
  def __init__(self):
    pass
  
  @abstractmethod
  def creator(self):
    'Return the creator name.'
    pass

  @abstractmethod
  def suck_level(self):
    'Return a number between 0 and 10 indicating how much this something sucks.'
    pass
