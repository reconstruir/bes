#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_options_desc import bcli_options_desc
from bes.bcli.bcli_simple_type_item_list import bcli_simple_type_item_list

class _unit_test_kiwi_options_desc(bcli_options_desc):

  def __init__(self):
    super().__init__()

  #@abstractmethod
  def name(self):
    return '_kiwi_options_desc'
  
  #@abstractmethod
  def types(self):
    return bcli_simple_type_item_list([
    ])

  #@abstractmethod
  def options_desc(self):
    return '''
kiwi int ${_var_foo}
pear int ${_var_bar}
'''
  
  #@abstractmethod
  def variables(self):
    return {
      '_var_foo': lambda: '42',
      '_var_bar': lambda: '666',
    }
