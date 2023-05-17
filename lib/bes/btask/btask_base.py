#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.enum_util.checked_int_enum import checked_int_enum

from .btask_i import btask_i

class btask_base(btask_i):

  def __init__(self):
    #from .btask_processor import btask_processor
    self.manager = None
    self.global_lock = None
'''
  def __getstate__(self):
    state = self.__dict__.copy()
    #del state['fun']
    return state
    
  def __setstate__(self, state):
    self.__dict__.update(state)  
'''

check.register_class(btask_base, name = 'btask', include_seq = False)
