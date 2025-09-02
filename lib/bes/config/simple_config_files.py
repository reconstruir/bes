#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from ..system.check import check
from bes.common.object_util import object_util
from bes.common.variable import variable
from bes.dependency.dependency_resolver import cyclic_dependency_error
from bes.dependency.dependency_resolver import dependency_resolver
from bes.dependency.dependency_resolver import missing_dependency_error
from bes.fs.file_util import file_util
from bes.system.host import host
from bes.system.log import logger

from ..files.bf_glob import bf_glob

from collections import namedtuple

from .simple_config import simple_config
from .simple_config_entry import simple_config_entry
from .simple_config_error import simple_config_error
from .simple_config_origin import simple_config_origin
from .simple_config_section import simple_config_section
from .simple_config_section_header import simple_config_section_header
  
class simple_config_files(object):
  'A class to manage finding and loading hierarchical config files.'

  _found_config = namedtuple('_found_config', 'where, filename, abs_path, config')

  _log = logger('simple_config')
  
  def __init__(self, search_path, glob_expression):
    self._search_path = self.parse_search_path(search_path)
    self._glob_expression = glob_expression
    self._configs = None
    self._dep_map = None
    self._resolved_sections = {}

  def __str__(self):
    return ','.join(self.files)

  @classmethod
  def parse_search_path(clazz, search_path):
    if check.is_string(search_path):
      result = search_path.split(os.pathsep)
    elif check.is_string_seq(search_path):
      result = [ x for x in search_path ]
    else:
      raise TypeError('Unkown type for search_path: {} - {}'.format(search_path, type(search_path)))
    return [ clazz._resolve_seach_path_part(part) for part in result ]
    
  @classmethod
  def _resolve_seach_path_part(clazz, part):
    substituted_part = variable.substitute(part, dict(os.environ), variable.BRACKET)
    return path.expanduser(substituted_part)
  
  def load(self):
    'Load the config files.  Will throw simple_config_error if any config file is invalid.'
    if self._configs:
      return
    self._configs = self._load_configs(self._search_path, self._glob_expression)
    self._dep_map, self._section_map = self._make_maps(self._configs)

  @property
  def has_loaded(self):
    'Return True if load() was called and suceeded.'
    return self._configs is not None
    
  @classmethod
  def _load_configs(clazz, search_path, glob_expression):
    result = []
    for next_path in search_path:
      for next_file in bf_glob.glob(next_path, glob_expression):
        filename = file_util.remove_head(next_file, next_path)
        config = simple_config.from_file(next_file, ignore_extends = True)
        result.append(clazz._found_config(next_path, filename, next_file, config))
    return result

  @classmethod
  def _make_maps(clazz, configs):
    dep_map = {}
    section_map = {}
    for config in configs:
      for section in config.config._sections:
        section_name = section.header_.name
        extends = set([ section.header_.extends ] if section.header_.extends else [])
        if section_name in extends:
          msg = 'Self dependency for {} in {}'.format(section_name,
                                                      section.origin_.source)
          raise simple_config_error(msg, section.origin_)
        if section_name in section_map:
          existing_section = section_map[section_name]
          msg = 'Duplicate config section "{}"\n  {}\n  {}'.format(section_name,
                                                                   section.origin_.source,
                                                                   existing_section.origin_.source)
          raise simple_config_error(msg, section.origin)
        section_map[section_name] = section
        dep_map[section_name] = extends
    return dep_map, section_map

  def _resolve_deps(self, section_name):
    resolved_deps = dependency_resolver.resolve_deps(self._dep_map, [ section_name ])
    all_deps_in_order = dependency_resolver.build_order_flat(self._dep_map)
    deps_in_order = [ dep for dep in all_deps_in_order if dep in resolved_deps ]
    return deps_in_order

  def section(self, section_name):
    '''
    Return a section object.  The section is constructed using any sections
    and dependencies specified in any config files found.
    '''
    if not section_name in self._resolved_sections:
      self._resolved_sections[section_name] = self._resolve_section(section_name)
    return self._resolved_sections[section_name]
  
  def _resolve_section(self, section_name):
    'Resolve a section using dependencies.'
    origin = simple_config_origin('\n'.join(self.files), None)
    try:
      deps = self._resolve_deps(section_name)
    except missing_dependency_error as ex:
      raise simple_config_error(ex.message, origin)
    except cyclic_dependency_error as ex:
      raise simple_config_error(ex.message, origin)
    except:
      raise
    
    entries = []
    for dep in deps:
      s = self._section_map[dep]
      for e in s:
        entries.append(e)
    entries = [ e for e in reversed(entries) ]
    seen = set()
    unique_entries = []
    for entry in entries:
      if not entry.value.key in seen:
        seen.add(entry.value.key)
        unique_entries.append(entry)
    header = simple_config_section_header(section_name, origin = origin)
    return simple_config_section(header, unique_entries, origin)

  @property
  def files(self):
    'Return a list of files loaded in load()'
    if not self.has_loaded:
      raise simple_config_error('Need to call load() first.', None)
    return sorted([ config.abs_path for config in self._configs ])

  def has_unique_section(self, section_name):
    'Return True if section_name is in any of the loaded config files.'
    if not self.has_loaded:
      raise simple_config_error('Need to call load() first.', None)
    return next((c for c in self._configs if c.config.has_unique_section(section_name)), None) is not None    

  @classmethod
  def load_and_find_section(clazz, config_path, section_name, extension):
    check.check_string(config_path)
    check.check_string(section_name)
    check.check_string(extension)

    clazz._log.log_d('load_and_find_section: config_path={} section_name={} extension={}'.format(config_path,
                                                                                                 section_name,
                                                                                                 extension))
    
    if config_path and not section_name:
      raise ValueError('section_name needs to be given when config_path is given.')
    if section_name and not config_path:
      raise ValueError('config_path needs to be given when section_name is given.')

    if not config_path:
      return None

    glob_expression = '*.{}'.format(extension)
    clazz._log.log_d('using config_path={} glob_expression={} section_name={}'.format(config_path,
                                                                                      glob_expression,
                                                                                      section_name))
    config = simple_config_files(config_path, glob_expression)
    config.load()
    if not config.files:
      raise simple_config_error('No config files matching "{}" in "{}"'.format(glob_expression, config_path))
    if not config.has_unique_section(section_name):
      raise simple_config_error('No config "{}" found in "{}":\n  {}'.format(section_name, config_path, '  \n'.join(config.files)))
    section = config.section(section_name)
    return section

  @classmethod
  def load_config(clazz, config):
    if not config:
      return {}
    clazz._log.log_d('load_config: config={}'.format(config))
    parsed_config = clazz._parse_config(config)
    clazz._log.log_d('load_config: parsed_config={}'.format(parsed_config))
    if parsed_config.section:
      section_name = parsed_config.section
    else:
      first_config = simple_config.from_file(parsed_config.filename, check_env_vars = True, ignore_extends = True)
      sections = first_config.section_names()
      if not sections:
        raise simple_config_error('No sections found in config: "{}"'.format(parsed_config.filename))
      section_name = sections[0]
    clazz._log.log_d('load_config: section_name={}'.format(section_name))
    config_path = path.dirname(parsed_config.filename)
    clazz._log.log_d('load_config: config_path={}'.format(config_path))
    return clazz.load_and_find_section(config_path, section_name, parsed_config.extension).to_dict()
    
  _parsed_config = namedtuple('_parsed_config', 'filename, section, extension')
  @classmethod
  def _parse_config(clazz, config):
    if not config:
      return None
    i = clazz._find_section_delimiter_index(config)
    if i < 0:
      return clazz._parsed_config(config, None, file_util.extension(config))
    filename = config[0:i]
    section = config[i+1:]
    return clazz._parsed_config(filename, section, file_util.extension(filename))

  @classmethod
  def _find_section_delimiter_index(clazz, config):
    if host.is_windows():
      _, filename = path.splitdrive(config)
    else:
      filename = config
    if ':' not in filename:
      return -1
    return config.rfind(':')
