#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system_command import system_command

from .vmware_error import vmware_error
from .vmware_app import vmware_app

class vmware_command_vmrun(system_command):

  @classmethod
  #@abstractmethod
  def exe_name(clazz):
    'The name of the executable.'
    return vmware_app.vmrun_exe_path()

  @classmethod
  #@abstractmethod
  def extra_path(clazz):
    'List of extra paths where to find the command.'
    return None

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    'The error exception class to raise when errors happen.'
    return vmware_error
  
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
