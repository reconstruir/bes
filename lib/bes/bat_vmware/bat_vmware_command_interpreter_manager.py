#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.system.host import host
from bes.common.singleton import singleton

from .bat_vmware_command_interpreter_registry import bat_vmware_command_interpreter_registry
from .bat_vmware_error import bat_vmware_error

from .bat_vmware_command_interpreters import *

@singleton
class bat_vmware_command_interpreter_manager(object):

  def __init__(self):
    self._map = {}
    self._add_registry_interpreters()

  def _add_registry_interpreters(self):
    for _, ci_class in bat_vmware_command_interpreter_registry.items():
      interpreter = ci_class()
      for system in interpreter.supported_systems():
        self.add_command_interpreter(system, interpreter)

  def add_command_interpreter(self, system, interpreter):
    check.check_string(system)
    check.check_bat_vmware_command_interpreter(interpreter)
    host.check_system(system)

    name = interpreter.name()
    supported_systems = interpreter.supported_systems()
    if not system in supported_systems:
      raise bat_vmware_error('Trying to add interpreter "{}" for a system it does not support "{}"'.format(name, system))
    
    if not system in self._map:
      self._map[system] = {}
    system_map = self._map[system]
    if name in system_map:
      raise bat_vmware_error('Trying to add interpreter with same name "{}": new={} old={}'.format(name,
                                                                                               interpreter,
                                                                                               system_map[name]))

    if interpreter.is_default():
      for next_name, next_interpreter in system_map.items():
        if next_interpreter.is_default():
          raise bat_vmware_error('Trying to add a different default interpreter: new={} old={}'.format(interpreter.name(),
                                                                                                   next_interpreter.name()))
    
    system_map[name] = interpreter
  
  def has_interpreter(self, system, name):
    check.check_string(system)
    check.check_string(name)
    host.check_system(system)

    return clazz.find_interpreter(system, name) != None
  
  def find_interpreter(self, system, name, raise_error = True):
    check.check_string(system)
    check.check_string(name)
    host.check_system(system)
    
    result = None
    if system in self._map:
      result = self._map[system].get(name, None)
    if not result and raise_error:
      raise bat_vmware_error('Interpreter for system "{}" not found: {}'.format(system, name))
    return result

  def find_default_interpreter(self, system, raise_error = True):
    check.check_string(system)
    host.check_system(system)

    result = None
    if system in self._map:
      system_map = self._map[system]
      for name, interpreter in system_map.items():
        if interpreter.is_default():
          result = interpreter
    if not result and raise_error:
      raise bat_vmware_error('Default interpreter for system "{}" not found'.format(system))
    return result

  def resolve_interpreter(self, system, name, raise_error = True):
    check.check_string(system)
    host.check_system(system)
    check.check_string(name, allow_none = True)

    if not name:
      interpreter = self.find_default_interpreter(system)
    else:
      interpreter = self.find_interpreter(system, name)

    if raise_error and not interpreter:
      raise bat_vmware_error('Failed to resolve interpreter "{}" for system {}'.format(name, system))
    
    return interpreter
