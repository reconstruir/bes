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
from bes.text.line_break import line_break

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
  
  def __init__(self,
               sections = None,
               source = None,
               check_env_vars = True,
               entry_formatter = None,
               section_finder = None):
    sections = sections or []
    source = source or '<unknown>'
    self._origin = simple_config_origin(source, 1)
    self._sections = sections[:]
    self._check_env_vars = check_env_vars
    self._entry_formatter = entry_formatter
    self._section_finder = section_finder

  def __str__(self):
    return self.to_string()

  def to_string(self):
    buf = StringIO()
    for i, section in enumerate(self._sections):
      if i != 0:
        buf.write(line_break.DEFAULT_LINE_BREAK)
      buf.write(section.to_string(entry_formatter = self._entry_formatter))
    return buf.getvalue()
  
  def __getattr__(self, section_name):
    return self.find(section_name)

  def __iter__(self):
    return iter(self._sections)
  
  def __hasattr__(self, section_name):
    return self.find(section_name) != None
    
  def add_section(self, section_name, extends = None, origin = None, extra_text = None):
    check.check_string(section_name)

    header = simple_config_section_header(section_name, extends = extends, extra_text = extra_text, origin = origin)
    section = simple_config_section(header, None, origin)
    self._sections.append(section)
    return section

  @classmethod
  def default_section_matcher(clazz, section, pattern):
    check.check_simple_config_section(section)
    check.check_string(pattern)

    return section.header_.name == pattern
  
  def remove_section(self, section_name, matcher = None):
    check.check_string(section_name)
    check.check_function(matcher, allow_none = True)

    matcher = matcher or self.default_section_matcher
    for i, section in enumerate(self._sections):
      if matcher(section, section_name):
        return self._sections.pop(i)
    raise simple_config_error('no such section found: "{}"'.format(section_name, self._origin))

  def has_unique_section(self, section_name, matcher = None):
    check.check_string(section_name)
    check.check_function(matcher, allow_none = True)

    matcher = matcher or self.default_section_matcher
    for section in self._sections:
      if matcher(section, section_name):
        return True
    return False

  def find_first_section(self, section_name, matcher = None):
    check.check_string(section_name)
    check.check_function(matcher, allow_none = True)

    matcher = matcher or self.default_section_matcher
    for section in self._sections:
      if matcher(section, section_name):
        return section
    return None
  
  def find_all_sections(self, section_name, raise_error = True, matcher = None):
    check.check_string(section_name)
    check.check_function(matcher, allow_none = True)

    matcher = matcher or self.default_section_matcher
    result = []
    for section in self._sections:
      if matcher(section, section_name):
        result.append(section)

    if not result and raise_error:
      raise simple_config_error('no sections found: "{}"'.format(section_name), self._origin)

    return result

  def find(self, section_name, matcher = None):
    check.check_string(section_name)
    check.check_function(matcher, allow_none = True)

    return self.section(section_name, matcher = matcher)

  def find_section_by_key_value(self, key, value):
    'Return a list of all the sections that have a key with value'
    check.check_string(key)
    check.check_string(value)

    result = []
    for section in self._sections:
      if section.has_key(key) and section.get_value(key) == value:
        result.append(section.header_.name)
    return result
  
  def section(self, section_name, matcher = None):
    check.check_string(section_name)
    check.check_function(matcher, allow_none = True)

    check.check_string(section_name)
    if not self.has_unique_section(section_name, matcher = matcher):
      self.add_section(section_name)
    sections = self.find_all_sections(section_name, matcher = matcher)
    if len(sections) != 1:
      raise simple_config_error('multiple sections found: {}'.format(section_name), self._origin)
    return sections[0]
  
  def get_value_string_list(self, section, key):
    value = self.get_value(section, key)
    return string_list.parse(value)
  
  def get_value(self, section, key):
    sections = self.find_all_sections(section)
    if len(sections) != 1:
      raise simple_config_error('multiple sections found: %s' % (section), self._origin)
    return sections[0].get_value(key)
  
  @classmethod
  def from_file(clazz,
                filename,
                check_env_vars = True,
                entry_parser = None,
                entry_formatter = None,
                ignore_extends = False):
    return clazz.from_text(file_util.read(filename, codec = 'utf8'),
                           source = filename,
                           check_env_vars = check_env_vars,
                           entry_parser = entry_parser,
                           entry_formatter = entry_formatter,
                           ignore_extends = ignore_extends)
    
  @classmethod
  def from_text(clazz,
                text,
                source = None,
                check_env_vars = True,
                entry_parser = None,
                entry_formatter = None,
                ignore_extends = False):
    check.check_string(text)
    source = source or '<unknown>'
    root = tree_text_parser.parse(text, strip_comments = True, root_name = 'root')
    return clazz.from_node(root,
                           source = source,
                           check_env_vars = check_env_vars,
                           entry_parser = entry_parser,
                           entry_formatter = entry_formatter,
                           ignore_extends = ignore_extends)

  @classmethod
  def from_node(clazz,
                node,
                source = None,
                check_env_vars = True,
                entry_parser = None,
                entry_formatter = None,
                ignore_extends = False):
    check.check_node(node)
    check.check_bool(check_env_vars)
    check.check_function(entry_parser, allow_none = True)
    check.check_bool(ignore_extends)

    source = source or '<unknown>'
    entry_parser = entry_parser or clazz._parse_entry
    sections = []
    section_dict = {}
    for child in node.children:
      origin = simple_config_origin(source, child.data.line_number)
      header = simple_config_section_header.parse_text(child.data.text, origin)

      extends_section = None
      if not ignore_extends and header.extends:
        extends_section = section_dict.get(header.extends, None)
        if not extends_section:
          msg = 'no extends section "{}" found for "{}"'.format(header.extends, header.name)
          raise simple_config_error(msg, origin)
      section = clazz._parse_section(child, source, entry_parser, origin, header, extends_section)
      sections.append(section)
      section_dict[section.header_.name] = section
    return simple_config(sections = sections,
                         source = source,
                         check_env_vars = check_env_vars,
                         entry_formatter = entry_formatter)
  
  @classmethod
  def _parse_section(clazz, node, source, entry_parser, origin, header, extends_section):
    check.check_node(node)
    check.check_string(source)
    check.check_function(entry_parser)
    check.check_simple_config_origin(origin)
    check.check_simple_config_section_header(header)
    check.check_simple_config_section(extends_section, allow_none = True)

    entries = clazz._parse_section_entries(node, source, entry_parser)
    return simple_config_section(header, entries, origin, extends_section_ = extends_section)

  @classmethod
  def _parse_section_entries(clazz, node, source, entry_parser):
    check.check_node(node)
    check.check_string(source)
    
    result = []
    for child in node.children:
      entry_origin = simple_config_origin(source, child.data.line_number)
      text = child.get_text(child.NODE_FLAT, delimiter = line_break.DEFAULT_LINE_BREAK)
      new_entry = entry_parser(text, entry_origin)
      result.append(new_entry)
    return result
  
  _ENTRY_KEY_VALID_FIRST_CHAR = string.ascii_letters + '_'
  _ENTRY_KEY_VALID_NEXT_CHARS = string.ascii_letters + string.digits + '_' + '*' + '?' + '-'
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
        raise simple_config_error('invalid config entry char "{}" (key should have only ascii letter, digits or underscore): "{}"'.format(c, text), origin)
      
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
