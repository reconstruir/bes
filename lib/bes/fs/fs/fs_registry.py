#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.factory.singleton_class_registry import singleton_class_registry
from bes.common.check import check
from bes.python.code import code
from bes.fs.temp_file import temp_file

from .fs_error import fs_error
from .fs_config import fs_config

class fs_registry(singleton_class_registry):
  __registry_class_name_prefix__ = 'bes_fs_'
  __registry_raise_on_existing__ = False

  @classmethod
  def load_from_config_file(clazz, config_filename):
    check.check_string(config_filename)
    config = fs_config.load(config_filename)

    values = copy.deepcopy(config.values)
    
    load_code = values.get('load_code', None)
    if load_code:
      load_filename = temp_file.make_temp_file(suffix = '.py', content = load_code)
      code.execfile(load_filename, globals(), locals())
      del values['load_code']
    
    fs_class = clazz.get(config.fs_type)

    if not fs_class:
      raise fs_error('Unkown filesystem type: {}'.format(config.fs_type))

    fields = fs_class.creation_fields()
    dfields = clazz._fields_to_dict(fields)

    # Make sure all the optional fields have a default None value
    for field in fields:
      if field.optional and not field.key in values:
        values[field.key] = None

    # Make sure all required values are given
    for field in fields:
      if not field.optional and not field.key in values:
        raise fs_error('Required field "{}" missing for filesystem {}'.format(field.key, config.fs_type))

    # Make sure all values are known and of valid type
    for key, value in values.items():
      field = dfields.get(key, None)
      if field is None:
        raise fs_error('Unkown field "{}" for filesystem {}'.format(key, config.fs_type))
      if field.checker_function:
        if not (field.optional and value is None):
          if not field.checker_function(value):
            raise fs_error('Invalid value "{}" for field "{} for filesystem {}'.format(value, key, config.fs_type))
      
    return fs_class.create(**values)

  @classmethod
  def _fields_to_dict(clazz, fields):
    result = {}
    for field in fields:
      result[field.key] = field
    return result
