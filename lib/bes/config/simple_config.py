#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from bes.common import check
from bes.compat import StringIO
from bes.key_value import key_value, key_value_list
from bes.fs import file_util
from bes.text import tree_text_parser
from bes.common import check, dict_util, variable
from bes.system import os_env_var

from collections import namedtuple

class error(Exception):
  def __init__(self, message, origin):
    super(error, self).__init__()
    self.message = message
    self.origin = origin

  def __str__(self):
    source = '<unknown>' if not self.origin else self.origin.source
    line_number = '<unknown>' if not self.origin else self.origin.line_number
    return '%s:%s: %s' % (source, line_number, self.message)

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

class config_section(namedtuple('config_section', 'name, entries, origin')):

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

  def find_by_key(self, key, raise_error = True, resolve_env_vars = False):
    for entry in self.entries:
      if entry.value.key == key:
        value = entry.value.value
        if resolve_env_vars:
          value = self._resolve_variable(value, entry.origin)
        return value
    if raise_error:
      raise error('%s not found' % (key), self.origin)
    return None
  
  def to_key_value_list(self, resolve_env_vars = False):
    'Return values as a key_value_list optionally resolving environment variables.'
    result = key_value_list()
    for entry in self.entries:
      value = entry.value.value
      if resolve_env_vars:
        value = self._resolve_variable(value, entry.origin)
      result.append(key_value(entry.value.key, value))
    return result
  
  def to_dict(self, resolve_env_vars = False):
    'Return values as a dict optionally resolving environment variables.'
    return self.to_key_value_list(resolve_env_vars = resolve_env_vars).to_dict()

  @classmethod
  def _resolve_variable(clazz, value, origin):
    variables = variable.find_variables(value)
    if variables:
      substitutions = clazz._substitutions_for_value(value, origin)
      return variable.substitute(value, substitutions, word_boundary = True)
    return value
  
  @classmethod
  def _substitutions_for_value(clazz, v, origin):
    result = {}
    variables = variable.find_variables(v)
    for var in variables:
      os_var = os_env_var(var)
      if not os_var.is_set:
        raise error('Not set in the current environment: %s' % (v), origin)
      result[var] = os_var.value
    return result
  
check.register_class(config_section)

class simple_config(object):
  'A very simple config file'

  # Convenience reference so users dont need to import error to catch it
  error = error
  
  def __init__(self, sections = None, source = None):
    sections = sections or []
    source = source or '<unknown>'
    log.add_logging(self, 'simple_config')
    self.origin = origin(source, 1)
    self.sections = sections[:]
    
  def __str__(self):
    buf = StringIO()
    for i, section in enumerate(self.sections):
      if i != 0:
        buf.write('\n')
      buf.write(str(section))
    return buf.getvalue()

  def add_section(self, section):
    check.check_config_section(section)
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
    return config_section(name, entries, origin(source, node.data.line_number))
    
  @classmethod
  def _parse_section_entries(clazz, node, source):
    check.check_node(node)
    check.check_string(source)
    result = []
    for child in node.children:
      entry_value = key_value.parse(child.data.text, delimiter = ':')
      entry_origin = origin(source, child.data.line_number)
      new_entry = entry(entry_value, entry_origin)
      result.append(new_entry)
    return result
