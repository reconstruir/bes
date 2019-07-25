#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.common.check import check
from bes.config.simple_config import simple_config
from bes.fs.file_util import file_util
from bes.system.log import logger

from .fs_error import fs_error

class fs_config(namedtuple('fs_config', 'fs_type, values')):
  'Filesystem configuration.'

  log = logger('fs_config')
  
  def __new__(clazz, fs_type, values):
    check.check_string(fs_type)
    check.check_dict(values, check.STRING_TYPES, check.STRING_TYPES)
    return clazz.__bases__[0].__new__(clazz, fs_type, values)

  @classmethod
  def load(clazz, config_filename):
    if not path.isfile(config_filename):
      raise fs_error('config_filename not found: {}'.format(config_filename))
    config = simple_config.from_file(config_filename)
    sections = config.find_sections('fsconfig')
    if not sections:
      raise fs_error('no fsconfig section found: {}'.format(config_filename))
    if len(sections) != 1:
      raise fs_error('only one fsconfig section should be given: {}'.format(config_filename))
    values = sections[0].to_key_value_list().to_dict()
    fs_type = values.get('fs_type', None)
    if fs_type is None:
      raise fs_error('no fs_type found in fsconfig: {}'.format(config_filename))
    del values['fs_type']
    return fs_config(fs_type, values)

check.register_class(fs_config, include_seq = False)
  
