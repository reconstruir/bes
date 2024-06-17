 #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import os
 
from bes.system.check import check
from bes.property.cached_property import cached_property

from .bcli_option_desc_item_list import bcli_option_desc_item_list
from .bcli_simple_type_item_list import bcli_simple_type_item_list
from .bcli_simple_type_manager import bcli_simple_type_manager
from .bcli_options_desc_i import bcli_options_desc_i

class bcli_options_desc(bcli_options_desc_i):

  def __init__(self):
    check.check_string(self.name())
    
    types = self.types()
    check.check_bcli_simple_type_item_list(types, allow_none = True)
    types = types[:]
    
    variables = self.variables()
    check.check_dict(variables, key_type = str)
    variables = copy.deepcopy(variables) if variables else {}

    defaults = self.defaults()
    check.check_dict(defaults, key_type = str)
    defaults = copy.deepcopy(defaults) if defaults else {}
    
    self._manager = bcli_simple_type_manager()
    self._manager.add_types(types)
    self._manager.add_variables(variables)
    self._manager.add_defaults(defaults)

  #@abstractmethod
  def types(self):
    return None
    
  #@abstractmethod
  def variables(self):
    return {}

  #@abstractmethod
  def defaults(self):
    return {}
  
  @cached_property
  def items(self):
    options_desc = self.options_desc() or ''
    check.check_string(options_desc)
    return bcli_option_desc_item_list.parse_text(self._manager, options_desc)
    
  @cached_property
  def items_dict(self):
    return self.items.to_dict()

  def has_option(self, name):
    check.check_string(name)
    return name in self.items_dict

  def default(self, name):
    check.check_string(name)
    
    assert self.has_option
    return self.items_dict[name].default

  def secret(self, name):
    check.check_string(name)
    
    assert self.has_option
    return self.items_dict[name].secret
  
  def check_value_type(self, name, value):
    check.check_string(name)
    assert name in self.items_dict
    item = self.items_dict[name]
    return self._manager.check_instance(value, item.option_type)

  def keys(self):
    return tuple(sorted([ key for key in self.items_dict.keys() ]))
  
  @classmethod
  def combine_options_desc(clazz, desc_text1, desc_text2):
    return desc_text1 + os.linesep + desc_text2

  @classmethod
  def combine_variables(clazz, variables1, variables2):
    result = copy.deepcopy(variables1)
    result.update(variables2)
    return result
  
check.register_class(bcli_options_desc, include_seq = False)
