#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.host import host

from bes.bat_vmware.vmware_command_interpreter import vmware_command_interpreter

class ci_unix_shell(vmware_command_interpreter):

  def __init__(self, name, full_path, is_default):
    check.check_string(name)
    check.check_string(full_path)
    check.check_bool(is_default)
    
    self._name = name
    self._full_path = full_path
    self._is_default = is_default

  #@abstractmethod
  def name(self):
    'Name for this interpreter.'
    return self._name

  #@abstractmethod
  def is_default(self):
    'Return True if this command interpreter is the default.'
    return self._is_default
  
  #@abstractmethod
  def supported_systems(self):
    'Return a tuple of supported systems.'
    return ( host.MACOS, host.LINUX )
  
  #@abstractmethod
  def full_path(self):
    'Return the full path of the interpreter in the vm'
    return self._full_path

  #@abstractmethod
  def build_command(self, script_text):
    'Build a command and return a command object for it'
    check.check_string(script_text)
    
    full_path = self.full_path()
    return self.command(full_path, script_text)
