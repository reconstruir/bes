#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.system_command import system_command

from .lsof_error import lsof_error

class lsof_command(system_command):

  #@abstractmethod
  def exe_name(self):
    'The name of the executable.'
    return 'lsof'

  #@abstractmethod
  def extra_path(self):
    'List of extra paths where to find the command.'
    return None

  #@abstractmethod
  def error_class(self):
    'The error exception class to raise when errors happen.'
    return lsof_error
  
  #@abstractmethod
  def static_args(self):
    'List of static arg for all calls of the command.'
    return ( '-w', )

  #@abstractmethod
  def supported_systems(self):
    'Return a list of supported systems.'
    return ( 'linux', 'macos' )
  
