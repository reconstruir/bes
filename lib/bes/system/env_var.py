#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from .check import check
from .log import logger
from .shell_path import shell_path

class env_var(object):

  _log = logger('env_var')
  
  def __init__(self, target, name):
    check.check(target, ( dict, os._Environ )) #check.STRING_TYPES, check.STRING_TYPES)
    check.check_string(name)
    
    self._target = target
    self._name = name
    self._log.log_d(f'__init__: target={target} name={name}')

  @property
  def name(self):
    return self._name

  @property
  def value(self):
    #return self._target.get(self._name, None)
    value = self._target.get(self._name, None)
    self._log.log_d(f'value.getter: value={value} - {type(value)}')
    if value == None:
      return None
    if not check.is_string(value):
      msg = f'Invalid value {value} - {type(value)} for key {self._name}'
      self._log.log_e(msg)
      raise ValueError(msg)
    return value

  @value.setter
  def value(self, value):
    check.check_string(value)
    
    self._log.log_d(f'value.setter: value={value} - {type(value)}')
    self._target[self._name] = value

  @property
  def path(self):
    value = self.value
    if not value:
      return []
    assert check.is_string(value)
    parts = shell_path.split(value)
    unique_parts = shell_path.unique_parts(parts)
    self._log.log_d(f'path.getter: parts={parts} unique_parts={unique_parts}')
    return unique_parts

  @path.setter
  def path(self, parts):
    if not parts:
      self.value = ''
      return
    if not check.is_seq(parts):
      raise TypeError(f'parts should be a sequence of strings: {parts} - {type(parts)}')
    for part in parts:
      if not check.is_string(part):
        raise TypeError(f'part should be a string: {part} - {type(part)}')
    
    unique_parts = shell_path.unique_parts(parts)
    self._log.log_d(f'path.setter: parts={parts} unique_parts={unique_parts}')
    self.value = self.path_join(unique_parts)

  def cleanup(self):
    self.path = self.path # the setter for path does the cleanup

  def append(self, p):
    self.value = shell_path.append(self.value, p)

  def remove(self, p):
    self.value = shell_path.remove(self.value, p)
    
  def prepend(self, p):
    self.value = shell_path.prepend(self.value, p)

  @classmethod
  def path_cleanup(clazz, parts):
    return shell_path.unique_parts(parts)

  @classmethod
  def path_split(clazz, p):
    return shell_path.split(p)

  @classmethod
  def path_join(clazz, l):
    return shell_path.join(l)

  def get(self, name, default_value = None):
    return self._target.get(name, default_value)
  
  @property
  def is_set(self):
    return self._name in self._target
  
  def unset(self):
    if self._name in self._target:
      del self._target[self._name]

  @property
  def value_if_set(self):
    if not self.is_set:
      return None
    return self.value
      
class os_env_var(env_var):
  def __init__(self, name):
    super(os_env_var, self).__init__(os.environ, name)
