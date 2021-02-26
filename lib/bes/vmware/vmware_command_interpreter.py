#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from abc import abstractmethod, ABCMeta

from bes.common.check import check
from bes.key_value.key_value_list import key_value_list
from bes.system.compat import compat
from bes.system.compat import with_metaclass

from .vmware_command_interpreter_registry import vmware_command_interpreter_registry

class _computer_setup_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name not in [ 'vmware_command_interpreter', 'vmware_command_unix_shell' ]:
      vmware_command_interpreter_registry.register(clazz)
    return clazz
  
class vmware_command_interpreter(with_metaclass(_computer_setup_register_meta, object)):

  @classmethod
  @abstractmethod
  def is_super_class(clazz):
    'Return True if this command interpreter class is a super class for other classes.'
    raise NotImplemented('is_super_class')
  
  @abstractmethod
  def name(self):
    'Name for this interpreter.'
    raise NotImplemented('name')

  @abstractmethod
  def is_default(self):
    'Return True if this command interpreter is the default.'
    raise NotImplemented('is_default')
  
  @abstractmethod
  def supported_systems(self):
    'Return a tuple of supported systems.'
    raise NotImplemented('supported_systems')
  
  @abstractmethod
  def full_path(self):
    'Return the full path of the interpreter in the vm'
    raise NotImplemented('interpreter_path')

  command = namedtuple('command', 'interpreter_path, script_text')
  @abstractmethod
  def build_command(self, script_text):
    'Build a command and return a command object for it'
    raise NotImplemented('build_command')
  
check.register_class(vmware_command_interpreter, include_seq = False)
