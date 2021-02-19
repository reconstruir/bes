# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
import os.path as path

from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.common.dict_util import dict_util
from bes.common.check import check
from bes.config.simple_config import simple_config
from bes.system.log import logger

class cli_options(with_metaclass(ABCMeta, object)):

  _log = logger('cli_options')
  
  def __init__(self, **kargs):
    default_values = self.default_values()
    self._log.log_d('default_values={}'.format(pprint.pformat(default_values)))
    self.update_values(default_values)
    config_values = self._read_config_file(kargs)
    self._log.log_d('config_values={}'.format(pprint.pformat(config_values)))
    self.update_values(config_values)
    self._log.log_d('kargs={}'.format(pprint.pformat(kargs)))
    non_default_kargs = self._extract_non_default_values(kargs, default_values)
    self._log.log_d('non_default_kargs={}'.format(pprint.pformat(non_default_kargs)))
    self.update_values(non_default_kargs)

  def __str__(self):
    d = dict_util.hide_passwords(self.__dict__, self.sensitive_keys())
    return pprint.pformat(d)
    
  @abstractmethod
  def default_values(self):
    'Return a dict of default values for these options.'
    raise NotImplemented('default_values')

  @abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    raise NotImplemented('check_value_types')

  @abstractmethod
  def sensitive_keys(self):
    'Return list of keys that are secrets and should be protected from __str__.'
    raise NotImplemented('sensitive_keys')

  @abstractmethod
  def value_type_hints(self):
    raise NotImplemented('morph_value_types')

  @abstractmethod
  def config_file_key(self):
    raise NotImplemented('config_file_key')

  @abstractmethod
  def config_file_section(self):
    raise NotImplemented('config_file_section')

  @abstractmethod
  def error_class(self):
    raise NotImplemented('error_class')
  
  @classmethod
  def _morph_value_type(clazz, values, key, type_class):
    if key in values:
      values[key] = type_class(values[key])
  
  def _valid_keys(self):
    'Return a list of valid keys for values in these options'
    return [ key for key in self.__dict__.keys() ]

  def update_values(self, values):
    'Update the options values and check their types'
    check.check_dict(values)
    
    for key, value in values.items():
      setattr(self, key, value)
    self.check_value_types()

  def _read_config_file(self, cli_values):
    check.check_dict(cli_values)

    config_file_key = self.config_file_key()
    if not config_file_key:
      return {}
    
    config_filename = None
    if config_file_key in cli_values:
      config_filename = cli_values[config_file_key]
      del cli_values[config_file_key]

    if config_filename == None:
      return {}

    error_class = self.error_class()
    if not path.exists(config_filename):
      raise error_class('Config file not found: "{}"'.format(config_filename))
      
    if not path.isfile(config_filename):
      raise error_class('Config file is not a file: "{}"'.format(config_filename))

    try:
      config = simple_config.from_file(config_filename)
    except Exception as ex:
      raise error_class(str(ex))

    config_file_section = self.config_file_section()
    if not config.has_section(config_file_section):
      raise error_class('No section "{}" found in config file: "{}"'.format(config_file_section,
                                                                                  config_filename))
    section = config.section(config_file_section)
    values = section.to_dict()

    for hint_key, hint_class in self.value_type_hints().items():
      self._morph_value_type(values, hint_key, hint_class)
      
    filtered_values = dict_util.filter_with_keys(values, self._valid_keys())
    return filtered_values

  def _extract_non_default_values(clazz, values, default_values):
    result = {}
    for key, value in values.items():
      if key in default_values:
        default_value = default_values[key]
        if value != default_value:
          result[key] = value
    return result
  
