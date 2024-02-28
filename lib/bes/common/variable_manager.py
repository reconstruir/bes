#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint

from os import path

from ..system.check import check
from ..system.environment import environment

from .variable import variable

class variable_manager(object):

  def __init__(self, variables = None, add_system_variables = True):
    self.variables = copy.deepcopy(variables or {})
    if add_system_variables:
      self._add_system_variables()

  def __str__(self):
    return pprint.pformat(self.variables)

  def add_variable(self, key, value):
    check.check_string(key)
    check.check_string(value)
    self.variables[key] = value
    
  def add_variables(self, variables):
    if check.is_key_value_list(variables):
      for kv in variables:
        self.variables[kv.key] = kv.value
    elif check.is_dict(variables):
      for key, value in variables.items():
        self.variables[key] = value
    else:
      raise ValueError('Unknown variables type: %s' % (type(variables)))
      
  def substitute(self, text, word_boundary = True):
    check.check_string(text)

    return variable.substitute(text, self.variables)

  def _add_system_variables(self):
    self.variables['HOME'] = path.expanduser('~')
    self.variables['USER'] = environment.username()

  def update_variable(self, key, value):
    check.check_string(key)
    check.check_string(value)
    self.variables[key] = value
    
  def update_variables(self, variables):
    if check.is_key_value_list(variables):
      for kv in variables:
        self.variables[kv.key] = kv.value
    elif check.is_dict(variables):
      for key, value in variables.items():
        self.variables[key] = value
    else:
      raise ValueError('Unknown variables type: %s' % (type(variables)))
    
check.register_class(variable_manager, include_seq = False)
