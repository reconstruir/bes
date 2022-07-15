#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.factory.singleton_class_registry import singleton_class_registry
from ..system.check import check
from bes.python.code import code
from bes.fs.temp_file import temp_file

from .vfs_error import vfs_error
from .vfs_config import vfs_config

# Not used directly but need to be imported so the factory knows about them
#from .vfs_local import vfs_local
#from .vfs_git_repo import vfs_git_repo

class vfs_registry(singleton_class_registry):
  __registry_class_name_prefix__ = 'bes_fs_'
  __registry_raise_on_existing__ = False

  @classmethod
  def load_from_config_file(clazz, config_filename):
    check.check_string(config_filename)
    config = vfs_config.load(config_filename)

    values = copy.deepcopy(config.values)

    vfs_class_path = values.get('vfs_class_path', None)
    if vfs_class_path:
      load_code = 'from {} import {}'.format(vfs_class_path, vfs_class_path.split('.')[-1])
      load_filename = temp_file.make_temp_file(suffix = '.py', content = load_code)
      code.execfile(load_filename, globals(), locals())
      del values['vfs_class_path']

    fs_type = config.fs_type
    fs_class = clazz.get(config.fs_type)
    if not fs_class:
      fs_class = clazz.get('vfs_' + config.fs_type)
      
    if not fs_class:
      raise vfs_error('Unkown filesystem type: {}'.format(config.fs_type))

    fields = fs_class.creation_fields()
    dfields = clazz._fields_to_dict(fields)

    # Make sure all the optional fields have a default None value
    for field in fields:
      if field.optional and not field.key in values:
        values[field.key] = None

    # Make sure all required values are given
    for field in fields:
      if not field.optional and not field.key in values:
        raise vfs_error('Required field "{}" missing for filesystem {}'.format(field.key, config.fs_type))

    # Make sure all values are known and of valid type
    for key, value in values.items():
      field = dfields.get(key, None)
      if field is None:
        raise vfs_error('Unkown field "{}" for filesystem {}'.format(key, config.fs_type))
      if field.checker_function:
        if not (field.optional and value is None):
          if not field.checker_function(value):
            raise vfs_error('Invalid value "{}" for field "{} for filesystem {}'.format(value, key, config.fs_type))
    return fs_class.create(config_filename, **values)

  @classmethod
  def _fields_to_dict(clazz, fields):
    result = {}
    for field in fields:
      result[field.key] = field
    return result
