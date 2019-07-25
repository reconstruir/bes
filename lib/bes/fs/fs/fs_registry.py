#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.factory.singleton_class_registry import singleton_class_registry
from bes.common.check import check

from .fs_error import fs_error
from .fs_config import fs_config

class fs_registry(singleton_class_registry):
  __registry_class_name_prefix__ = 'bes_fs_'
  __registry_raise_on_existing__ = False

  @classmethod
  def load_from_config_file(clazz, config_filename):
    check.check_string(config_filename)
    config = fs_config.load(config_filename)
    fs_class = clazz.get(config.fs_type)
    if not fs_class:
      raise fs_error('Unkown filesystem type: {}'.format(config.fs_type))
    return fs_class.create(config)
