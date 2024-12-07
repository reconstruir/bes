 #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import os
 
from bes.common.dict_util import dict_util
from bes.system.check import check
from bes.system.log import logger
from bes.property.cached_property import cached_property
from bes.common.json_util import json_util

from .bcli_option_desc_item_list import bcli_option_desc_item_list
from .bcli_type_i import bcli_type_i
from .bcli_type_manager import bcli_type_manager
from .bcli_options_desc_i import bcli_options_desc_i

class bcli_options_desc(bcli_options_desc_i):

  _log = logger('bcli')
  
  def __init__(self):
    types = self.types or []
    for t in types:
      if not issubclass(t, bcli_type_i):
        raise TypeError(f't should be a subclass of bcli_type_i instead of "{t}".')
    
    variables = self.variables or {}
    check.check_dict(variables, key_type = str)
    variables = copy.deepcopy(variables)

    self._manager = bcli_type_manager()
    self._manager.add_types(types[:])
    self._manager.add_variables(variables)

  def to_json(self):
    return self._manager.to_json()
    
  #@abstractmethod
  def _types(self):
    return None

  @cached_property
  def types(self):
    return self._types()
  
  #@abstractmethod
  def _variables(self):
    return None

  @cached_property
  def variables(self):
    return self._variables()
  
  #@abstractmethod
  def _error_class(self):
    return RuntimeError

  @cached_property
  def error_class(self):
    return self._error_class()

  @cached_property
  def options_desc(self):
    return self._options_desc()
  
  @cached_property
  def items(self):
    options_desc = self.options_desc # or ''
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
  
  def check_value_type(self, name, value, desc_item):
    check.check_string(name)
    check.check_bcli_option_desc_item(desc_item, allow_none = True)

    self._log.log_method_d()
    
    assert name in self.items_dict
    item = self.items_dict[name]

#    print(f'item={item}')
#    print(f'desc_item={desc_item}')
    
#    if item.option_type.check_function:
#      return item.option_type.check_function(value, allow_none = True)
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
