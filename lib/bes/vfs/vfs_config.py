#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from ..system.check import check
from bes.config.simple_config import simple_config
from bes.fs.file_util import file_util
from bes.system.log import logger

from .vfs_error import vfs_error

class vfs_config(namedtuple('vfs_config', 'fs_type, values')):
  'Filesystem configuration.'

  log = logger('vfs_config')
  
  def __new__(clazz, fs_type, values):
    check.check_string(fs_type)
    check.check_dict(values, check.STRING_TYPES, check.STRING_TYPES)
    return clazz.__bases__[0].__new__(clazz, fs_type, values)

  @classmethod
  def load(clazz, config_filename):
    if not path.isfile(config_filename):
      raise vfs_error('config_filename not found: {}'.format(config_filename))
    config = simple_config.from_file(config_filename)
    sections = config.find_all_sections('fsconfig')
    if not sections:
      raise vfs_error('no fsconfig section found: {}'.format(config_filename))
    if len(sections) != 1:
      raise vfs_error('only one fsconfig section should be given: {}'.format(config_filename))
    values = sections[0].to_key_value_list(resolve_env_vars = True).to_dict()
    fs_type = values.get('vfs_type', None)
    if fs_type is None:
      raise vfs_error('no fs_type found in fsconfig: {}'.format(config_filename))
    del values['vfs_type']
    return vfs_config(fs_type, values)

check.register_class(vfs_config, include_seq = False)
  
