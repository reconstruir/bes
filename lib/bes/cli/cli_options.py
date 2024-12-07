# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint
import json
import os.path as path

from ..common.bool_util import bool_util
from ..common.dict_util import dict_util
from ..common.json_util import json_util
from ..common.string_util import string_util
from ..config.simple_config import simple_config
from ..config.simple_config_editor import simple_config_editor
from ..system.check import check
from ..system.log import logger
from ..system.os_env import os_env_var
from ..text.string_lexer_options import string_lexer_options
from ..text.string_list import string_list

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
    return pprint.pformat(self.to_dict())
    
  def to_dict(self, hide_sensitive_keys = True):
    if hide_sensitive_keys:
      sensitive_keys = self.sensitive_keys() or {}
      d = dict_util.hide_passwords(self.__dict__, sensitive_keys)
    else:
      d = copy.deepcopy(self.__dict__)
    return d

  def to_json(self, hide_sensitive_keys = True):
    d = self.to_dict(hide_sensitive_keys = hide_sensitive_keys)
    return json_util.to_json(d, indent = 2, sort_keys = True, ensure_last_line_sep = True)

  @classmethod
  def from_json(clazz, text):
    check.check_string(text)
    
    d = json.loads(text)
    return clazz(**d)
  
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
    cast_value = self._cast_value_if_needed(value, type_hint)
    setattr(self, key, cast_value)

  @classmethod
  def _cast_value_if_needed(clazz, value, type_hint):
    if not type_hint:
      return value
    if value == None:
      return value
    if type_hint == bool:
      return bool_util.parse_bool(value)
    elif type_hint == list:
      if check.is_string(value):
        value = string_list.parse(value, options = string_lexer_options.KEEP_QUOTES).to_list()
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
    values = section.to_dict(resolve_env_vars = not clazz.ignore_config_file_variables())

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
  def _collect_super_method_values(clazz, method_name):
    'Collect all the results of the mro classes for the given method.'
    check.check_string(method_name)

    ignore_classes = {
      cli_options_base,
      cli_options,
      object,
      clazz,
    }
    result = []
    classes = [ c for c in clazz.__mro__ if not c in ignore_classes ]
    for next_class in classes:
      next_method = getattr(next_class, method_name, None)
      if next_method:
        next_values = next_method()
        result.append(next_values)
    return result
  
  @classmethod
  def _call_super_method_dict(clazz, method_name, values):
    'Call all the superclasses method.'
    check.check_string(method_name)
    check.check_dict(values, allow_none = True)

    values = values or {}
    result = {}
    collected_values = clazz._collect_super_method_values(method_name)
    for next_values in collected_values:
      assert isinstance(next_values, dict)
      result.update(next_values)
    result.update(values)
    return result

  @classmethod
  def _call_super_method_tuple(clazz, method_name, values):
    'Call all the superclasses method.'
    check.check_string(method_name)
    check.check_tuple(values, allow_none = True)

    values = values or ()
    result = ()
    collected_values = clazz._collect_super_method_values(method_name)
    for next_values in collected_values:
      assert isinstance(next_values, tuple)
      result += next_values
    result += values
    return result
  
  @classmethod
  def super_default_values(clazz, values = None):
    'Return a dict of defaults for these options.'
    check.check_dict(values, allow_none = True)

    return clazz._call_super_method_dict('default_values', values)
  
  @classmethod
  def super_value_type_hints(clazz, values = None):
    'Return a dict of defaults for these options.'
    check.check_dict(values, allow_none = True)

    return clazz._call_super_method_dict('value_type_hints', values)

  @classmethod
  def super_sensitive_keys(clazz, values):
    'Return a dict of defaults for these options.'
    check.check_tuple(values, allow_none = True)

    return clazz._call_super_method_tuple('sensitive_keys', values)

  def clone(self):
    d = self.to_dict(hide_sensitive_keys = False)
    return self.__class__(**d)
  
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
