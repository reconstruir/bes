#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.common.check import check

class simple_config_variables(object):

  def __init__(self):
    self._variables = {}

  def __iter__(self):
    return iter(self._variables)

  def __getitem__(self, key):
    return self._variables.__getitem__(key)
    
  def __setitem__(self, key, value):
    self._variables.__setitem__(key, value)
  
  def set_variable(self, key, value):
    check.check_string(key)
    check.check_value(value)

    self._variables[key] = value

  def set_variables(self, variables):
    check.check_dict(variables, check.STRING_TYPES, check.STRING_TYPES)

    self._variables = copy.deepcopy(variables)
    
  def update_variables(self, variables):
    check.check_dict(variables, check.STRING_TYPES, check.STRING_TYPES)

    self._variables.update(variables)
    
  def variables(self):
    return copy.deepcopy(self._variables)

check.register_class(simple_config_variables)
