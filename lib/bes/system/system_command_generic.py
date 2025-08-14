#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .check import check
from .system_command import system_command
from .system_error import system_error

class system_command_generic(system_command):
  'A generic system command.'

  def __init__(self, exe_name, extra_path = None, error_class = None,
               static_args = None, supported_systems = None):
    self.__class__._exe_name = exe_name
    self.__class__._extra_path = extra_path
    self.__class__._error_class = error_class or system_error
    self.__class__._static_args = static_args
    self.__class__._supported_systems = supported_systems or ( 'linux', 'macos', 'windows' )
  
  @classmethod
  #@abstractmethod
  def exe_name(clazz):
    'The name of the executable.'
    return clazz._exe_name

  @classmethod
  #@abstractmethod
  def extra_path(clazz):
    'List of extra paths where to find the command.'
    return clazz._extra_path

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    'The error exception class to raise when errors happen.'
    return clazz._error_class
  
  @classmethod
  #@abstractmethod
  def static_args(clazz):
    'List of static arg for all calls of the command.'
    return clazz._static_args

  @classmethod
  #@abstractmethod
  def supported_systems(clazz):
    'Return a list of supported systems.'
    return clazz._supported_systems
  
check.register_class(system_command_generic, include_seq = False)
