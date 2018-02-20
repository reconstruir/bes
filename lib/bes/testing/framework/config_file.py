#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple
from bes.common import string_util
from bes.text import comments, lines
from bes.fs import file_find

class config_file(object):

  bescfg = namedtuple('bescfg', 'root_dir,configs,dep_map,env_dirs')

  @classmethod
  def load_configs(clazz, d):
    root_dir = path.abspath(d)
    configs = {}
    config_files = config_file.find_config_files(root_dir)
    env_dirs = {}
    for f in config_files:
      config = config_file.read_config_file(f)
      configs[config['name']] = config
      env_dirs[path.join(config['root_dir'], 'env')] = config
    dep_map = clazz._make_dep_map(configs)
    return clazz.bescfg(root_dir, configs, dep_map, env_dirs)
    
  @classmethod
  def _make_dep_map(clazz, configs):
    dep_map = {}
    for name, config in configs.items():
      dep_map[name] = set(config.get('requires', []))
    return dep_map
    
  @classmethod
  def find_config_files(clazz, d):
    return file_find.find_fnmatch(d, [ '*.bescfg' ], relative = False, min_depth = None, max_depth = 4):
  
  @classmethod
  def read_config_file(clazz, filename):
    filename = path.abspath(filename)
    root = path.normpath(path.join(path.dirname(filename), '..'))
    content = file_util.read(filename)
    config = clazz.parse(content)
    variables = {
      'root': root,
      'rebuild_dir': path.expanduser('~/.rebuild'),
    }
    config = clazz.substitute_variables(config, variables)
    config['filename'] = filename
    config['root_dir'] = root
    return config
    
  @classmethod
  def parse(clazz, s):
    result = {}
    lines = s.split('\n')
    lines = [ comments.strip_line(line) for line in lines ]
    lines = [ line.strip() for line in lines ]
    lines = [ line for line in lines if line ]
    for line in lines:
      key, sep, value = line.partition(':')
      assert sep == ':'
      key = key.strip()
      value = value.strip()
      if key == 'requires':
        value = tuple(sorted(string_util.split_by_white_space(value)))
      elif key in [ 'PATH', 'PYTHONPATH' ]:
        value = value.split(':')
      assert key not in result
      result[key] = value
    return result

  @classmethod
  def substitute_variables(clazz, config, variables):
    assert isinstance(config, dict)
    assert isinstance(variables, dict)
    result = copy.deepcopy(config)
    for key in config.keys():
      clazz._sub_one(result, key, variables)
    return result
    
  @classmethod
  def _sub_one(clazz, config, key, variables):
    assert isinstance(config, dict)
    assert isinstance(key, basestring)
    assert isinstance(variables, dict)
    value = config[key]
    for var_name, var_value in variables.items():
      sub_key = '${%s}' % (var_name)
      value = clazz._replace_value(value, sub_key, var_value)
    config[key] = value
    
  @classmethod
  def _replace_value(clazz, value, sub_key, sub_value):
    assert isinstance(value, ( basestring, tuple, list ) )
    assert isinstance(sub_key, basestring)
    assert isinstance(sub_value, basestring)
    if isinstance(value, basestring):
      return value.replace(sub_key, sub_value)
    elif isinstance(value, tuple):
      return tuple([ x.replace(sub_key, sub_value) for x in value ])
    elif isinstance(value, list):
      return [ x.replace(sub_key, sub_value) for x in value ]
