#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from bes.common import check
from bes.compat import StringIO
from bes.key_value import key_value, key_value_list
from bes.fs import file_util
from bes.text import tree_text_parser

from collections import namedtuple

class error(Exception):
  def __init__(self, message, origin):
    super(error, self).__init__()
    self.message = message
    self.origin = origin

  def __str__(self):
    return '%s:%s: %s' % (self.origin.source, self.origin.line_number, self.message)

class origin(namedtuple('origin', 'source, line_number')):

  def __new__(clazz, source, line_number):
    check.check_string(source)
    check.check_int(line_number)
    return clazz.__bases__[0].__new__(clazz, source, line_number)

check.register_class(origin)
  
class entry(namedtuple('entry', 'value, origin')):

  def __new__(clazz, value, origin):
    check.check_key_value(value)
    check.check_origin(origin)
    return clazz.__bases__[0].__new__(clazz, value, origin)

  def __str__(self):
    return self.value.to_string(delimiter = ':', quote_value = False)
  
check.register_class(entry)

class section(namedtuple('section', 'name, entries, origin')):

  def __new__(clazz, name, entries, origin):
    check.check_string(name)
    check.check_entry_seq(entries)
    check.check_origin(origin)
    return clazz.__bases__[0].__new__(clazz, name, entries, origin)

  def __str__(self):
    buf = StringIO()
    buf.write(self.name)
    buf.write('\n')
    for i, entry in enumerate(self.entries):
      if i != 0:
        buf.write('\n')
      buf.write('  ')
      buf.write(str(entry))
    return buf.getvalue()

  def find_by_key(self, key, raise_error = True):
    for entry in self.entries:
      if entry.value.key == key:
        return entry.value.value
    if raise_error:
      raise error('%s not found' % (key), self.origin)
    return None
  
  def to_key_value_list(self):
    return key_value_list([ entry.value for entry in self.entries ])
  
  def to_dict(self):
    return self.to_key_value_list().to_dict()
  
check.register_class(section)

class simple_config(object):
  'A very simple config file'

  def __init__(self, sections = None):
    sections = sections or []
    log.add_logging(self, 'simple_config')
    self.sections = sections[:]
    
  def __str__(self):
    buf = StringIO()
    for i, section in enumerate(self.sections):
      if i != 0:
        buf.write('\n')
      buf.write(str(section))
    return buf.getvalue()

  def add_section(self, section):
    check.check_section(section)
    self.sections.append(section)

  def find_sections(self, name, raise_error = True):
    check.check_string(name)
    result = [ section for section in self.sections if section.name == name ]
    if not result and raise_error:
      raise error('no sections found: %s' % (name), self.origin)
    return result

  @classmethod
  def from_file(clazz, filename):
    return clazz.from_text(file_util.read(filename), source = filename)
    
  @classmethod
  def from_text(clazz, s, source = None):
    check.check_string(s)
    source = source or '<unknown>'
    root = tree_text_parser.parse(s, strip_comments = True, root_name = 'root')
    sections = []
    for child in root.children:
      section = clazz._parse_section(child, source)
      sections.append(section)
    return clazz(sections = sections)

  @classmethod
  def _parse_section(clazz, node, source):
    check.check_node(node)
    check.check_string(source)
    name = node.data.text
    entries = clazz._parse_section_entries(node, source)
    return section(name, entries, origin(source, node.data.line_number))
    
  @classmethod
  def _parse_section_entries(clazz, node, source):
    check.check_node(node)
    check.check_string(source)
    result = []
    for child in node.children:
      entry_value = key_value.parse(child.data.text, delimiter = ':')
      entry_origin = origin(source, child.data.line_number)
      entry(entry_value, entry_origin)
      result.append(entry(entry_value, entry_origin))
    return result
