#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system_command import system_command

from .bat_vmware_error import bat_vmware_error
from .bat_vmware_app import bat_vmware_app

class bat_vmware_command_vmrun(system_command):

  @classmethod
  #@abstractmethod
  def exe_name(clazz):
    'The name of the executable.'
    return bat_vmware_app.vmrun_exe_path()

  @classmethod
  #@abstractmethod
  def extra_path(clazz):
    'List of extra paths where to find the command.'
    return None

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    'The error exception class to raise when errors happen.'
    return bat_vmware_error
  
  @classmethod
  #@abstractmethod
  def static_args(clazz):
    'List of static arg for all calls of the command.'
    return None

  @classmethod
  #@abstractmethod
  def supported_systems(clazz):
    'Return a list of supported systems.'
    return ( 'linux', 'macos', 'windows' )
