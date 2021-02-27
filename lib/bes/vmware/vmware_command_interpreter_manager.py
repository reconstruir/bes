#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.host import host

from .vmware_command_interpreter_registry import vmware_command_interpreter_registry
from .vmware_error import vmware_error

from .command_interpreters import *

class vmware_command_interpreter_manager(object):

  def __init__(self):
    self._map = {}
    self._add_registry_interpreters()

  def _add_registry_interpreters(self):
    for _, ci_class in vmware_command_interpreter_registry.items():
      interpreter = ci_class()
      for system in interpreter.supported_systems():
        self.add_command_interpreter(system, interpreter)

  def add_command_interpreter(self, system, interpreter):
    check.check_string(system)
    check.check_vmware_command_interpreter(interpreter)
    host.check_system(system)

    name = interpreter.name()
    supported_systems = interpreter.supported_systems()
    if not system in supported_systems:
      raise vmware_error('Trying to add interpreter "{}" for a system it does not support "{}"'.format(name, system))
    
    if not system in self._map:
      self._map[system] = {}
    system_map = self._map[system]
    if name in system_map:
      raise vmware_error('Trying to add interpreter with same name "{}": new={} old={}'.format(name,
                                                                                               interpreter,
                                                                                               system_map[name]))
    system_map[name] = interpreter
  
  def has_interpreter(self, system, name):
    check.check_string(system)
    check.check_string(name)
    host.check_system(system)

    return clazz.find_interpreter(system, name) != None
  
  def find_interpreter(self, system, name):
    check.check_string(system)
    check.check_string(name)
    host.check_system(system)
    
    if not system in self._map:
      return False
    system_map = self._map[system]
    return system_map.get(name, None)

  def find_default_interpreter(self, system):
    check.check_string(system)
    host.check_system(system)
    
    if not system in self._map:
      return None
    system_map = self._map[system]
    result = []
    for name, interpreter in system_map.items():
      if interpreter.is_default():
        result.append(interpreter)
    if len(result) == 0:
      return None
    elif len(result) > 1:
      raise vmware_error('Multiple interpreters marked default found: {}'.format(' '.join([ i.name() for i in result ])))
    return result[0]

  def resolve_interpreter(self, system, name):
    check.check_string(system)
    host.check_system(system)
    check.check_string(name, allow_none = True)

    if not name:
      interpreter = self.find_default_interpreter(system)
    else:
      interpreter = self.find_interpreter(system, name)
    return interpreter
  
  x='''
  @classmethod
  def interpreter_is_valid(clazz, name):
    'Return True if this system interpreter is valid.'
    check.check_string(name)
    
    return name in clazz.interpreters()
  
  @classmethod
  def check_interpreter(clazz, name):
    'Raise an exception if the interpreter is not valid.'
    check.check_string(name)
    
    if not clazz.interpreter_is_valid(name):
      raise vmware_error('Invalid interpreter: "{}"  Should be one of: {}"'.format(name, ' '.join(clazz.interpreters())))
'''
