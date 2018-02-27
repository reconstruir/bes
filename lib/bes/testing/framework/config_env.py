#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple
from bes.compat import StringIO
from bes.common import check, string_util
from bes.text import comments, lines
from bes.fs import file_find, file_util

from .config_file import config_file

class config_env(object):

  def __init__(self, root_dir):
    if not root_dir:
      self.root_dir = None
      self.config_files = []
      self.config_map = {}
      self.dependency_map = {}
    else:
      self.root_dir = path.abspath(root_dir)
      config_filenames = self.find_config_files(self.root_dir)
      self.config_files = [ config_file(f) for f in config_filenames ]
      self.config_map = self._make_config_map(self.config_files)
      self.dependency_map = self._make_dep_map(self.config_map)

  def config_for_name(self, name):
    return self.config_map.get(name, None)
    
  def config_for_filename(self, filename):
    for name, config in self.config_map.items():
      if filename.startswith(config.root_dir):
        return config
    return None
    
  @classmethod
  def _make_config_map(clazz, config_files):
    config_map = {}
    for cf in config_files:
      name = cf.data.name
      if name in config_map:
        raise RuntimeError('Duplicate project \"%s\": %s %s' % (name, path.relpath(cf.filename),
                                                                path.relpath(config_map[name].filename)))
      config_map[name] = cf
    return config_map
  
  @classmethod
  def _make_dep_map(clazz, configs):
    dep_map = {}
    for name, cf in configs.items():
      dep_map[name] = cf.data.requires
    return dep_map

  @classmethod
  def find_config_files(clazz, d):
    return file_find.find_fnmatch(d, [ '*.bescfg' ], relative = False, min_depth = None, max_depth = 4)
  
