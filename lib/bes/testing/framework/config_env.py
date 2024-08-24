#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, glob, os, os.path as path

from bes.common.algorithm import algorithm
from bes.dependency.dependency_resolver import dependency_resolver
from bes.fs.file_find import file_find
from bes.fs.file_path import file_path
from bes.system.env_var import os_env_var
from bes.system.host import host

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
      config_filenames = self._find_config_files(self.root_dir)
      self.config_files = [ config_file(f) for f in config_filenames ]
      self.config_map = self._make_config_map(self.config_files)
      self.dependency_map = self._make_dep_map(self.config_map)
      
  def config_for_name(self, name):
    return self.config_map.get(name, None)
    
  def config_for_filename(self, filename):
    for name, config in self.config_map.items():
      if filename.startswith(config.root_dir + os.sep):
        return config
    return None
    
  @classmethod
  def _make_config_map(clazz, config_files):
    config_map = {}
    for cf in config_files:
      name = cf.data.name
      if name in config_map:
        raise RuntimeError('Duplicate project \"%s\": %s %s' % (name, cf.filename,
                                                                config_map[name].filename))
      config_map[name] = cf
    return config_map
  
  @classmethod
  def _make_dep_map(clazz, configs):
    dep_map = {}
    for name, cf in configs.items():
      dep_map[name] = cf.data.requires
    return dep_map

  @classmethod
  def _find_config_files(clazz, d):
    in_root = clazz._find_config_files_in_root(d)
    in_env = clazz._find_config_files_in_env()
    # On windows theres a silly bug in os.walk() that makes the directory names
    # be lower case so normalize the case before making the list unique
    if host.is_windows():
      in_env_set = set([ f.lower() for f in in_env ])
      in_root = [ f for f in in_root if f.lower() not in in_env_set ]
    return algorithm.unique(sorted(in_root + in_env))

  @classmethod
  def _find_config_files_in_root(clazz, d):
    if os_env_var('BESTEST_SKIP_ENV').is_set:
      return []
    return file_find.find_fnmatch(d, [ '*.bescfg' ], relative = False, min_depth = None, max_depth = 3)

  @classmethod
  def _find_config_files_in_env(clazz):
    return file_path.glob(os_env_var('BESTEST_CONFIG_PATH').path, '*.bescfg')

  def resolve_deps(self, names):
    return dependency_resolver.resolve_deps(self.dependency_map, names)
