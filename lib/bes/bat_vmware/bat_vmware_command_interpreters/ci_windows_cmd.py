#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.host import host

from bes.vmware.vmware_command_interpreter import vmware_command_interpreter

class ci_windows_cmd(vmware_command_interpreter):

  def __init__(self):
    pass

  #@abstractmethod
  def name(self):
    'Name for this interpreter.'
    return 'cmd'

  #@abstractmethod
  def is_default(self):
    'Return True if this command interpreter is the default.'
    return True
  
  #@abstractmethod
  def supported_systems(self):
    'Return a tuple of supported systems.'
    return ( host.WINDOWS, )
  
  #@abstractmethod
  def full_path(self):
    'Return the full path of the interpreter in the vm'
    return r'C:\Windows\System32\cmd.exe'

  #@abstractmethod
  def build_command(self, script_text):
    'Build a command and return a command object for it'
    check.check_string(script_text)
    
    full_path = self.full_path()
    command_script_text = r'{} /C "{}"'.format(full_path, script_text)
    return self.command('', command_script_text)
