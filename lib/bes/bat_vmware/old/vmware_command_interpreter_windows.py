#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .vmware_command_interpreter_base import vmware_command_interpreter_base
from .vmware_error import vmware_error

class vmware_command_interpreter_windows(vmware_command_interpreter_base):

  _INTERPRETER_PATHS = {
    'cmd': r'C:\Windows\System32\cmd.exe',
    'powershell': r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',
  }
  
  @classmethod
  #@abstractmethod
  def interpreters(clazz):
    'Return a tuple of all the available interpreters in the system'
    return tuple([ key for key in clazz._INTERPRETER_PATHS.keys()])

  @classmethod
  #@abstractmethod
  def default_interpreter(clazz):
    'Return the default interpreter'
    return 'cmd'
  
  @classmethod
  #@abstractmethod
  def interpreter_path(clazz, name):
    'Return the full path to the named interpreter'
    interpreter_path = clazz._INTERPRETER_PATHS.get(name, None)
    if not interpreter_path:
      raise vmware_error('Unknown interpreter "{}".  Should be one of: {}'.format(name, ' '.join(clazz.interpreters())))
    return interpreter_path
  
  @classmethod
  #@abstractmethod
  def build_command(clazz, name, script_text):
    'Build a command and return a command object for it'
    interpreter_path = clazz.interpreter_path(name)
    command_script_text = r'{} /C "{}"'.format(interpreter_path, script_text)
    return clazz.command('', command_script_text)
