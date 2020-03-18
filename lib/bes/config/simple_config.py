#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string, re

from bes.common.check import check
from bes.compat.StringIO import StringIO
from bes.fs.file_util import file_util
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.system.log import logger
from bes.text.tree_text_parser import tree_text_parser
from bes.text.string_list import string_list

from collections import namedtuple

from .simple_config_entry import simple_config_entry
from .simple_config_error import simple_config_error
from .simple_config_origin import simple_config_origin
from .simple_config_section import simple_config_section
from .simple_config_section_header import simple_config_section_header
  
class simple_config(object):
  '''
  A very simple config file in this form:

  ---------
  # Comment support
  section
    key1: value1
    key2: value2
    key3: ${ENV_VALUE3}
    key4: ~/.foo/something.txt # more comment support

  basic
    color: red
    flavor: tart

  # support for extending sections with full dependency checking and resolution
  fancy extends basic
    flavor: spicy
  ---------
  '''

  log = logger('simple_config')
  
  # Convenience reference so users dont need to import error to catch it
  error = simple_config_error
  
  def __init__(self, sections = None, source = None, check_env_vars = True):
    sections = sections or []
    source = source or '<unknown>'
    self._origin = simple_config_origin(source, 1)
    self._sections = sections[:]
    self._check_env_vars = check_env_vars

  def __str__(self):
    buf = StringIO()
    for i, section in enumerate(self._sections):
      if i != 0:
        buf.write('\n')
      buf.write(str(section))
    return buf.getvalue()

  def __getattr__(self, section_name):
    return self.find(section_name)

  def __iter__(self):
    return iter(self._sections)
  
  def __hasattr__(self, section_name):
    return self.find(section_name) != None
    
  def add_section(self, section, extends = None, origin = None):
    check.check_string(section)

    header = simple_config_section_header(section, extends = extends, origin = origin)
    section = simple_config_section(header, None, origin)
    self._sections.append(section)
    return section

  def remove_section(self, section_name):
    check.check_string(section_name)

    for i, section in enumerate(self._sections):
      if section.header_.name == section_name:
        return self._sections.pop(i)
    raise simple_config_error('no such section found: "{}"'.format(section_name, self._origin))

  def has_section(self, name):
    check.check_string(name)
    return next((section for section in self._sections if section.header_.name == name), None) is not None
    
  def find_sections(self, name, raise_error = True):
    check.check_string(name)
    result = [ section for section in self._sections if section.header_.name == name ]
    if not result and raise_error:
      raise simple_config_error('no sections found: %s' % (name), self._origin)
    return result

  def find(self, section_name):
    return self.section(section_name)
  
  def section(self, section_name):
    check.check_string(section_name)
    if not self.has_section(section_name):
      self.add_section(section_name)
    sections = self.find_sections(section_name)
    if len(sections) != 1:
      raise simple_config_error('multiple sections found: {}'.format(section_name), self._origin)
    return sections[0]
  
  def get_value(self, section, key):
    return self.find(section).get_value(key)
  
  def get_value_string_list(self, section, key):
    value = self.get_value(section, key)
    return string_list.parse(value)

  def get_value(self, section, key):
    sections = self.find_sections(section)
    if len(sections) != 1:
      raise simple_config_error('multiple sections found: %s' % (section), self._origin)
    return sections[0].get_value(key)
  
  @classmethod
  def from_file(clazz, filename, check_env_vars = True):
    return clazz.from_text(file_util.read(filename, codec = 'utf8'),
                           source = filename,
                           check_env_vars = check_env_vars)
    
  @classmethod
  def from_text(clazz, s, source = None, check_env_vars = True):
    check.check_string(s)
    source = source or '<unknown>'
    root = tree_text_parser.parse(s, strip_comments = True, root_name = 'root')
    return clazz.from_node(root, source = source, check_env_vars = check_env_vars)

  @classmethod
  def from_node(clazz, node, source = None, check_env_vars = True):
    check.check_node(node)
    source = source or '<unknown>'
    sections = []
    for child in node.children:
      section = clazz._parse_section(child, source)
      sections.append(section)
    return simple_config(sections = sections, source = source, check_env_vars = check_env_vars)
  
  @classmethod
  def _parse_section(clazz, node, source):
    check.check_node(node)
    check.check_string(source)

    origin = simple_config_origin(source, node.data.line_number)
    header = simple_config_section_header.parse_text(node.data.text, origin)
    entries = clazz._parse_section_entries(node, source)
    return simple_config_section(header, entries, origin)

  @classmethod
  def _parse_section_entries(clazz, node, source):
    check.check_node(node)
    check.check_string(source)
    result = []
    for child in node.children:
      entry_origin = simple_config_origin(source, child.data.line_number)
      new_entry = clazz._parse_entry(child.data.text, entry_origin)
      result.append(new_entry)
    return result
  
  _ENTRY_KEY_VALID_FIRST_CHAR = string.ascii_letters + '_'
  _ENTRY_KEY_VALID_NEXT_CHARS = string.ascii_letters + string.digits + '_'
  @classmethod
  def _parse_entry(clazz, text, origin):
    check.check_string(text)
    check.check_simple_config_origin(origin)

    raw_key, delimiter, raw_value = text.partition(':')
    if delimiter != ':':
      raise simple_config_error('invalid config entry (missing colon): "{}"'.format(text), origin)
    raw_key = raw_key.strip()
    if not raw_key:
      raise simple_config_error('invalid config entry (empty key): "{}"'.format(text), origin)
    raw_value = raw_value.strip()

    key, raw_annotations = clazz._entry_partition_key_and_annotation(raw_key)
    
    if not key[0] in clazz._ENTRY_KEY_VALID_FIRST_CHAR:
      raise simple_config_error('invalid config entry (key should start with ascii letter or underscore): "{}"'.format(text), origin)

    for c in key[1:]:
      if not c in clazz._ENTRY_KEY_VALID_NEXT_CHARS:
        raise simple_config_error('invalid config entry (key should have only ascii letter, digits or underscore): "{}"'.format(text), origin)
      
    value = key_value(key, raw_value)
    annotations = clazz._parse_annotations(raw_annotations, origin)
    return simple_config_entry(value, origin, annotations = annotations)

  @classmethod
  def _entry_partition_key_and_annotation(clazz, raw_key):
    i = raw_key.find('[')
    if i < 0:
      return raw_key, None
    key = raw_key[0:i]
    annotations = raw_key[i:]
    return key, annotations
  
  @classmethod
  def _parse_annotations(clazz, text, origin):
    check.check_string(text, allow_none = True)
    check.check_simple_config_origin(origin)
    if not text:
      return None
    if not text.startswith('[') or not text.endswith(']'):
      raise simple_config_error('invalid annotation: "{}"'.format(text), origin)
    strings = [ s.strip() for s in text[1:-1].split(',') ]
    result = key_value_list()
    for s in strings:
      a = clazz._parse_annotation(s, origin)
      result.append(a)
    return result

  _ANNOTATION_PATTERN = re.compile('([a-zA-Z_]\w*)\s*(=\s*.*)?')
  @classmethod
  def _parse_annotation(clazz, text, origin):
    check.check_string(text)
    check.check_simple_config_origin(origin)

    parts = text.partition('=')
    key = parts[0].strip()
    if parts[1] == '=':
      value = parts[2].strip()
    else:
      value = None
    return key_value(key, value)

  def section_names(self):
    'Return a list of all the section names.  Multiple sections with the same name get repeated.'
    return [ section.header_.name for section in self._sections ]
    
  def sections_are_unique(self):
    'Return True if every section has a different name.'
    names = self.section_names()
    return len(set(names)) == len(names)
    
  def update(self, config):
    'Update from another config.  Only works for configs without multiple sections with the same name.'

    if not self.sections_are_unique():
      raise simple_config_error('update only works if sections have unique names.')

    if check.is_simple_config(config):
      self._update_with_simple_config(config)
    elif check.is_dict(config):
      self._update_with_dict(config)
    else:
      raise TypeError('config should be of simple_config or dict type: {}'.format(type(config)))

  def to_dict(self, resolve_env_vars = False):
    'Return the config as a dict.'

    if not self.sections_are_unique():
      raise simple_config_error('to_dict() only works if sections have unique names.')

    result = {}
    for section in self._sections:
      result[section.header_.name] = section.to_dict(resolve_env_vars = resolve_env_vars)
    return result
    
  def _update_with_simple_config(self, config):
    'Update from another config.  Only works for configs without multiple sections with the same name.'
    check.check_simple_config(config)

    if not config.sections_are_unique():
      raise simple_config_error('update only works if sections have unique names.')

    for other_section in config._sections:
      self_section = self.find(other_section.header_.name)
      self_section.set_values(other_section.to_dict(resolve_env_vars = False))
  
  def _update_with_dict(self, config):
    'Update from a dict of dicts.'
    check.check_dict(config, check.STRING_TYPES, dict)

    for section_name, values in config.items():
      self_section = self.find(section_name)
      self_section.set_values(values)
  
check.register_class(simple_config)
  
