#!/usr/bin/env python
#-*- coding:utf-8 -*-

from something_base import something_base

class something_linux(something_base):

  def __init__(self):
    super(something_linux, self).__init__()
    
  def creator(self):
    'Return the creator name.'
    return 'linus'

  def suck_level(self):
    'Return a number between 0 and 10 indicating how much this something sucks.'
    return 8
