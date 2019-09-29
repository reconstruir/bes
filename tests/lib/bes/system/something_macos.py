#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from something_base import something_base

class something_macos(something_base):

  def __init__(self):
    super(something_macos, self).__init__()
    
  def creator(self):
    'Return the creator name.'
    return 'steve'

  def suck_level(self):
    'Return a number between 0 and 10 indicating how much this something sucks.'
    return 9
