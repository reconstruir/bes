#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class environment_base(object, metaclass = ABCMeta):
  'Abstract interface for dealing with system specific non portable environment stuff.'
  
  @classmethod
  @abstractmethod
  def home_dir(clazz):
    'Return the current users home dir.'
    raise NotImplementedError('home_dir')

  @classmethod
  @abstractmethod
  def username(clazz):
    'Return the current users username.'
    raise NotImplementedError('username')
  
  @classmethod
  @abstractmethod
  def home_dir_env(clazz, home_dir):
    'Return a dict with the environment needed to set the home directory.'
    raise NotImplementedError('home_dir_env')
  
  @classmethod
  @abstractmethod
  def default_path(clazz):
    'The default system PATH.'
    raise NotImplementedError('default_path')
  
  @classmethod
  @abstractmethod
  def clean_path(clazz):
    'A clean system PATH with only the bare minimum needed to run shell commands.'
    raise NotImplementedError('clean_path')

  @classmethod
  @abstractmethod
  def clean_variables(clazz):
    'A list of variables clean system PATH with only the bare minimum needed to run shell commands.'
    raise NotImplementedError('clean_variables')
  
