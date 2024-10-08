# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

class cli_options_base(object, metaclass = ABCMeta):

  @classmethod
  @abstractmethod
  def default_values(clazz):
    'Return a dict of default values for these options.'
    raise NotImplemented('default_values')

  @classmethod
  @abstractmethod
  def sensitive_keys(clazz):
    'Return a tuple of keys that are secrets and should be protected from __str__.'
    raise NotImplemented('sensitive_keys')

  @classmethod
  @abstractmethod
  def value_type_hints(clazz):
    raise NotImplemented('morph_value_types')

  @classmethod
  @abstractmethod
  def config_file_key(clazz):
    raise NotImplemented('config_file_key')

  @classmethod
  @abstractmethod
  def config_file_env_var_name(clazz):
    raise NotImplemented('config_file_env_var_name')
  
  @classmethod
  @abstractmethod
  def config_file_section(clazz):
    raise NotImplemented('config_file_section')

  @classmethod
  @abstractmethod
  def error_class(clazz):
    raise NotImplemented('error_class')

  @abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    raise NotImplemented('check_value_types')

  @classmethod
  def ignore_config_file_variables(clazz):
    return False
  
