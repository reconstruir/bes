#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.system_command import system_command

from .brew_error import brew_error

class brew_command(system_command):

  #@abstractmethod
  def exe_name(self):
    'The name of the executable.'
    return 'brew'

  #@abstractmethod
  def extra_path(self):
    'List of extra paths where to find the command.'
    return None

  #@abstractmethod
  def error_class(self):
    'The error exception class to raise when errors happen.'
    return brew_error
  
  #@abstractmethod
  def static_args(self):
    'List of static arg for all calls of the command.'
    return None

  #@abstractmethod
  def supported_systems(self):
    'Return a list of supported systems.'
    return ( 'linux', 'macos' )
  
