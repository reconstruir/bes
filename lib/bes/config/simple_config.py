#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.compat.StringIO import StringIO
from bes.fs.file_util import file_util
from bes.key_value.key_value import key_value
from bes.system.log import log
from bes.text.tree_text_parser import tree_text_parser

from collections import namedtuple

from .simple_config_entry import simple_config_entry
from .simple_config_error import simple_config_error
from .simple_config_origin import simple_config_origin
from .simple_config_section import simple_config_section
from .simple_config_section_header import simple_config_section_header
  
class simple_config(object):
  'A very simple config file'

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

  def find_sections(self, name, raise_error = True):
    check.check_string(name)
    result = [ section for section in self.sections if section.name == name ]
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
    name = node.data.text
    entries = clazz._parse_section_entries(node, source)
    return simple_config_section(name, entries, simple_config_origin(source, node.data.line_number))

  @classmethod
  def _parse_section_header(clazz, node, text):
    name = node.data.text
  
  @classmethod
  def _parse_section_entries(clazz, node, source):
    check.check_node(node)
    check.check_string(source)
    result = []
    for child in node.children:
      entry_value = key_value.parse(child.data.text, delimiter = ':')
      entry_origin = simple_config_origin(source, child.data.line_number)
      new_entry = simple_config_entry(entry_value, entry_origin)
      result.append(new_entry)
    return result
