# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
import os.path as path

from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.config.simple_config import simple_config
from bes.config.simple_config_editor import simple_config_editor
from bes.system.log import logger
from bes.system.os_env import os_env_var
from bes.common.bool_util import bool_util

from .cli_options_base import cli_options_base

class cli_options(cli_options_base):

  _log = logger('cli_options')
  
  def __init__(self, **kargs):
    default_values = self.default_values()
    self._log.log_d('__init__: default_values={}'.format(pprint.pformat(default_values)))
    self._do_update_values(default_values)
    config_values = self._read_config_file(kargs)
    self._log.log_d('__init__: config_values={}'.format(pprint.pformat(config_values)))
    self._do_update_values(config_values)
    self._log.log_d('__init__: kargs={}'.format(pprint.pformat(kargs)))
    non_default_kargs = self._extract_valid_non_default_values(kargs, default_values)
    self._log.log_d('__init__: non_default_kargs={}'.format(pprint.pformat(non_default_kargs)))
    self._do_update_values(non_default_kargs)
    self.check_value_types()
    
  def __str__(self):
    sensitive_keys = self.sensitive_keys() or {}
    d = dict_util.hide_passwords(self.__dict__, sensitive_keys)
    return pprint.pformat(d)
    
  def _valid_keys(self):
    'Return a list of valid keys for values in these options'
    return [ key for key in self.__dict__.keys() ]

  def update_values(self, values):
    'Update the options values and check their types'
    check.check_dict(values)
    
    self._do_update_values(values)
    self.check_value_types()

  def _do_update_values(self, values):
    'update values only with no checking'
    self._log.log_d('_do_update_values: update before: {}'.format(str(self)))
    for key, value in values.items():
      self._do_set_value(key, value)
    self._log.log_d('_do_update_values: update after: {}'.format(str(self)))

  def _get_value_type_hint(self, key):
    if not _special_attributes.has_key(self.__class__, 'value_type_hints'):
      _special_attributes.set_value(self.__class__, 'value_type_hints', self.value_type_hints())
    value_type_hints = _special_attributes.get_value(self.__class__, 'value_type_hints', None)
    return value_type_hints.get(key, None)
    
  def _do_set_value(self, key, value):
    'update one value'
    self._log.log_d('_do_update_value: setattr({}, {}, {}:{})'.format(id(self), key, value, type(value)))
    type_hint = self._get_value_type_hint(key)
    value = self._cast_value_if_needed(value, type_hint)
    setattr(self, key, value)

  @classmethod
  def _cast_value_if_needed(clazz, value, type_hint):
    if not type_hint:
      return value
    if value == None:
      return value
    if type_hint == bool:
      return bool_util.parse_bool(value)
    return type_hint(value)
    
  @classmethod
  def _read_config_file(clazz, cli_values):
    check.check_dict(cli_values)

    clazz._log.log_d('_read_config_file: cli_values={}'.format(cli_values))
    
    config_filename = None    
    config_file_env_var_name = clazz.config_file_env_var_name()
    clazz._log.log_d('_read_config_file: config_file_env_var_name={}'.format(config_file_env_var_name))
    if config_file_env_var_name:
      v = os_env_var(config_file_env_var_name)
      if v.is_set:
        clazz._log.log_d('_read_config_file: using env config file {}'.format(v.value))
        config_filename = v.value
        
    if not config_filename:
      config_file_key = clazz.config_file_key()
      clazz._log.log_d('_read_config_file: config_file_key={}'.format(config_file_key))
      if not config_file_key:
        return {}
    
      if config_file_key in cli_values:
        config_filename = cli_values[config_file_key]
        clazz._log.log_d('_read_config_file: using config file {}'.format(config_filename))
        del cli_values[config_file_key]

    if config_filename == None:
      return {}
    clazz._log.log_d('_read_config_file: loading config file filename {}'.format(config_filename))
    if not _special_attributes.has_key(clazz, 'config_file'):
      ed = simple_config_editor(config_filename)
      _special_attributes.set_value(clazz, 'config_file', ed)
    return clazz._values_from_config_file(config_filename)

  def _extract_valid_non_default_values(clazz, values, default_values):
    'Extract and return only the valid non default values'
    result = {}
    for key, value in values.items():
      if key in default_values:
        default_value = default_values[key]
        if value != default_value:
          result[key] = value
    return result

  @classmethod
  def _values_from_config_file(clazz, config_filename):
    error_class = clazz.error_class()
    if not path.exists(config_filename):
      raise error_class('Config file not found: "{}"'.format(config_filename))
      
    if not path.isfile(config_filename):
      raise error_class('Config file is not a file: "{}"'.format(config_filename))

    try:
      config = simple_config.from_file(config_filename)
    except Exception as ex:
      raise error_class(str(ex))

    config_file_section = clazz.config_file_section()
    if not config.has_section(config_file_section):
      raise error_class('No section "{}" found in config file: "{}"'.format(config_file_section,
                                                                                  config_filename))
    section = config.section(config_file_section)
    values = section.to_dict()

    valid_keys = clazz.default_values().keys()
    filtered_values = dict_util.filter_with_keys(values, valid_keys)
    return filtered_values
  
  @classmethod
  def from_config_file(clazz, config_filename):
    values = clazz._values_from_config_file(config_filename)
    return clazz(**values)

  @property
  def config_file(self):
    return _special_attributes.get_value(self.__class__, 'config_file', None)


  @classmethod
  def _call_super_method(clazz, method_name, values):
    'Call all the superclasses method.'
    check.check_string(method_name)
    check.check_dict(values)

    IGNORE_CLASSES = {
      cli_options_base,
      cli_options,
      object,
    }
    result = {}
    classes = [ c for c in clazz.__mro__ if not c in IGNORE_CLASSES ]
    for c in classes:
      print('CLASS: {}'.format(c))
#    assert False
    for next_class in classes:
      next_method = getattr(next_class, method_name)
      if not next_method:
        error_class = clazz.error_class()
        raise error_class('Method "{}" not found in {}'.format(method_name, next_class))
      next_values = next_method()
      result.update(next_values)
    result.update(values)
    return result

  @classmethod
  def super_default_values(clazz, values):
    'Return a dict of defaults for these options.'
    check.check_dict(values)

    return dict_util.combine(super(clazz, clazz).default_values(), values)
  
  @classmethod
  def super_value_type_hints(clazz, values):
    'Return a dict of defaults for these options.'
    check.check_dict(values)

    return dict_util.combine(super(clazz, clazz).value_type_hints(), values)

  @classmethod
  def super_sensitive_keys(clazz, keys):
    'Return a dict of defaults for these options.'
    check.check_tuple(keys, allow_none = True)

    return super(clazz, clazz).sensitive_keys() or () + keys
  
  
class _special_attributes(object):
  '''
  Use a global dict to store special attributes to not pollute either
  self or self.__class__ attributes of cli_options otherwise attributes
  get confused with option ones
  '''

  _attribs = {}
  
  @classmethod
  def ensure_class(clazz, the_class):
    if not the_class in clazz._attribs:
      clazz._attribs[the_class] = {}

  @classmethod
  def has_key(clazz, the_class, key):
    clazz.ensure_class(the_class)
    return key in clazz._attribs[the_class]

  @classmethod
  def set_value(clazz, the_class, key, value):
    clazz.ensure_class(the_class)
    clazz._attribs[the_class][key] = value

  @classmethod
  def get_value(clazz, the_class, key, default_value):
    clazz.ensure_class(the_class)
    if not clazz.has_key(the_class, key):
      return None
    return clazz._attribs[the_class].get(key, default_value)

