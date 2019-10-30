#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.common.object_util import object_util
from bes.dependency.dependency_resolver import dependency_resolver

from collections import namedtuple

from .simple_config import simple_config
from .simple_config_entry import simple_config_entry
from .simple_config_error import simple_config_error
from .simple_config_origin import simple_config_origin
from .simple_config_section import simple_config_section
from .simple_config_section_header import simple_config_section_header
  
class simple_config_loader(object):
  'A class to manage finding and loading hierarchical config files.'

  _found_config = namedtuple('_found_config', 'where, filename, abs_path, config')
  
  def __init__(self, search_path, glob_expression):
    self._search_path = object_util.listify(search_path)
    self._glob_expression = glob_expression
    self._configs = None
    self._dep_map = None
    self._resolved_sections = {}
    
  def load(self):
    'Load the config files.  Will throw simple_config_error if any config file is invalid.'
    if self._configs:
      return
    self._configs = self.load_configs(self._search_path, self._glob_expression)
    self._dep_map, self._section_map = self._make_maps(self._configs)

  @property
  def has_loaded(self):
    'Return True if load() was called and suceeded.'
    return self._configs is not None
    
  @classmethod
  def load_configs(clazz, search_path, glob_expression):
    result = []
    for next_path in search_path:
      for next_file in file_path.glob(next_path, glob_expression):
        filename = file_util.remove_head(next_file, next_path)
        config = simple_config.from_file(next_file)
        result.append(clazz._found_config(next_path, filename, next_file, config))
    return result

  @classmethod
  def _make_maps(clazz, configs):
    dep_map = {}
    section_map = {}
    for config in configs:
      for section in config.config.sections:
        section_name = section.header.name
        extends = set([ section.header.extends ] if section.header.extends else [])
        if section_name in section_map:
          existing_section = section_map[section_name]
          msg = 'Duplicate config section "{}"\n  {}\n  {}'.format(section_name,
                                                                   section.origin.source,
                                                                   existing_section.origin.source)
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
    deps = self._resolve_deps(section_name)
    entries = []
    for dep in deps:
      s = self._section_map[dep]
      for e in s.entries:
        entries.append(e)
    entries = [ e for e in reversed(entries) ]
    seen = set()
    unique_entries = []
    for entry in entries:
      if not entry.value.key in seen:
        seen.add(entry.value.key)
        unique_entries.append(entry)
    origin = simple_config_origin('\n'.join(self.files), None)
    header = simple_config_section_header(section_name, None, origin)
    return simple_config_section(header, unique_entries, origin)

  @property
  def files(self):
    'Return a list of files loaded in load()'
    if not self.has_loaded:
      raise simple_config_error('Need to call load() first.', None)
    return sorted([ config.abs_path for config in self._configs ])
    
  
