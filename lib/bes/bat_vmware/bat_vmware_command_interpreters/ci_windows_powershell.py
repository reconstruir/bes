#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.host import host

from bes.bat_vmware.bat_vmware_command_interpreter import bat_vmware_command_interpreter

class ci_windows_powershell(bat_vmware_command_interpreter):

  def __init__(self):
    pass

  @classmethod
  #@abstractmethod
  def is_super_class(clazz):
    'Return True if this command interpreter class is a super class for other classes.'
    return False
  
  #@abstractmethod
  def name(self):
    'Name for this interpreter.'
    return 'powershell'

  #@abstractmethod
  def is_default(self):
    'Return True if this command interpreter is the default.'
    return False
  
  #@abstractmethod
  def supported_systems(self):
    'Return a tuple of supported systems.'
    return ( host.WINDOWS, )
  
  #@abstractmethod
  def full_path(self):
    'Return the full path of the interpreter in the vm'
    return r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'

  #@abstractmethod
  def build_command(self, script_text):
    'Build a command and return a command object for it'
    check.check_string(script_text)
    
    full_path = self.full_path()
    command_script_text = r'{} -Command "{}"'.format(full_path, script_text)
    return self.command('', command_script_text)
