#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.system_command import system_command

from .linux_attr_error import linux_attr_error

class linux_attr_command(system_command):

  @classmethod
  #@abstractmethod
  def exe_name(clazz):
    'The name of the executable.'
    return '/usr/bin/linux_attr'
  
  @classmethod
  #@abstractmethod
  def extra_path(clazz):
    'List of extra paths where to find the command.'
    return None

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    'The error exception class to raise when errors happen.'
    return linux_attr_error
  
  @classmethod
  #@abstractmethod
  def static_args(clazz):
    'List of static arg for all calls of the command.'
    return None

  @classmethod
  #@abstractmethod
  def supported_systems(clazz):
    'Return a list of supported systems.'
    return ( 'macos', )
