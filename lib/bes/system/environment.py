#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .host import host
from .log import logger

from ._detail.environment_base import environment_base

class environment(environment_base):

  _log = logger('environment')
  
  def _find_impl_class():
    result = None
    if host.is_unix():
      from ._detail.environment_unix import environment_unix
      result = environment_unix
    elif host.is_windows():
      from ._detail.environment_windows import environment_windows
      result = environment_windows
    return result
  
  _impl_class = _find_impl_class()
  if not _impl_class:
    host.raise_unsupported_system()
  
  def __init__(self):
    pass

  @classmethod
  #@abstractmethod
  def home_dir(clazz):
    'Return the current users home dir.'
    return clazz._impl_class.home_dir()
  
  @classmethod
  #@abstractmethod
  def home_dir_env(clazz, home_dir):
    'Return a dict with the environment needed to set the home directory.'
    return clazz._impl_class.home_dir_env(home_dir)

  @classmethod
  #@abstractmethod
  def default_path(clazz):
    'The default system PATH.'
    return clazz._impl_class.default_path()
  
  @classmethod
  #@abstractmethod
  def clean_path(clazz):
    'A clean system PATH with only the bare minimum needed to run shell commands.'
    return clazz._impl_class.clean_path()

  @classmethod
  #@abstractmethod
  def clean_variables(clazz):
    'A list of variables clean system PATH with only the bare minimum needed to run shell commands.'
    return clazz._impl_class.clean_variables()
