#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from abc import abstractmethod, ABCMeta
from ..system.check import check

from .bat_vmware_error import bat_vmware_error

class bat_vmware_command_interpreter_base(object, metaclass = ABCMeta):
  'Abstract interface for dealing with command interpreters in vms.'
  
  @classmethod
  @abstractmethod
  def interpreters(clazz):
    'Return a tuple of all the available interpreters in the system'
    raise NotImplemented('interpreters')

  @classmethod
  @abstractmethod
  def default_interpreter(clazz):
    'Return the default interpreter'
    raise NotImplemented('default_interpreter')
  
  @classmethod
  @abstractmethod
  def interpreter_path(clazz, name):
    'Return the full path to the named interpreter'
    raise NotImplemented('interpreter_path')

  command = namedtuple('command', 'interpreter_path, script_text')
  @classmethod
  @abstractmethod
  def build_command(clazz, name, script_text):
    'Build a command and return a command object for it'
    raise NotImplemented('build_command')

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
      raise bat_vmware_error('Invalid interpreter: "{}"  Should be one of: {}"'.format(name, ' '.join(clazz.interpreters())))
