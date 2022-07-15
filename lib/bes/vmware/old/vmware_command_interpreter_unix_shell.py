#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.system.host import host

from .vmware_command_interpreter import vmware_command_interpreter
from .vmware_error import vmware_error

class vmware_command_interpreter_unix_shell(vmware_command_interpreter):

  def __init__(self, name, full_path):
    check.check_string(name)
    check.check_string(full_path)
    
    self._name = name
    self._full_path = full_path

  #@abstractmethod
  def name(self):
    'Name for this interpreter.'
    return self._name

  #@abstractmethod
  def supported_systems(self):
    'Return a tuple of supported systems.'
    raise ( host.MACOS, host.LINUX )
  
  #@classmethod
  @abstractmethod
  def full_path(self):
    'Return the full path of the interpreter in the vm'
    return self._full_path

  #@abstractmethod
  def build_command(self, script_text):
    'Build a command and return a command object for it'
    check.check_string(script_text)
    
    full_path = clazz.full_path(name)
    command_script_text = r'-c "{}"'.format(script_text)
    return clazz.command(full_path, command_script_text)
