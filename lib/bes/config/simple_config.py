#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.common.check import check
from bes.compat.StringIO import StringIO
from bes.fs.file_util import file_util
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.system.log import log
from bes.text.tree_text_parser import tree_text_parser

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

  # Convenience reference so users dont need to import error to catch it
  error = simple_config_error
  
  def __init__(self, sections = None, source = None):
    sections = sections or []
    source = source or '<unknown>'
    log.add_logging(self, 'simple_config')
    self.origin = simple_config_origin(source, 1)
    self.sections = sections[:]
    
  def __str__(self):
    buf = StringIO()
    for i, section in enumerate(self.sections):
      if i != 0:
        buf.write('\n')
      buf.write(str(section))
    return buf.getvalue()

  def add_section(self, section):
    check.check_simple_config_section(section)
    self.sections.append(section)

  def has_section(self, name):
    check.check_string(name)
    return next((section for section in self.sections if section.header.name == name), None) is not None
    
  def find_sections(self, name, raise_error = True):
    check.check_string(name)
    result = [ section for section in self.sections if section.header.name == name ]
    if not result and raise_error:
      raise simple_config_error('no sections found: %s' % (name), self.origin)
    return result

  @classmethod
  def from_file(clazz, filename):
    return clazz.from_text(file_util.read(filename), source = filename)
    
  @classmethod
  def from_text(clazz, s, source = None):
    check.check_string(s)
    source = source or '<unknown>'
    root = tree_text_parser.parse(s, strip_comments = True, root_name = 'root')
    return clazz.from_node(root, source = source)

  @classmethod
  def from_node(clazz, node, source = None):
    check.check_node(node)
    source = source or '<unknown>'
    sections = []
    for child in node.children:
      section = clazz._parse_section(child, source)
      sections.append(section)
    return simple_config(sections = sections, source = source)
  
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
  
  _ENTRY_PATTERN = re.compile('([a-zA-Z_]\w*)(\[.*\])?\s*:\s*(.*)')
  @classmethod
  def _parse_entry(clazz, text, origin):
    check.check_string(text)
    check.check_simple_config_origin(origin)
    f = clazz._ENTRY_PATTERN.findall(text)
    if not f or len(f) != 1 or len(f[0]) != 3:
      raise simple_config_error('invalid config entry: "{}"'.format(text), origin)
    value = key_value(f[0][0].strip(), f[0][2].strip())
    annotations = clazz._parse_annotations(f[0][1], origin)
    return simple_config_entry(value, origin, annotations = annotations)

  @classmethod
  def _parse_annotations(clazz, text, origin):
    check.check_string(text)
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
