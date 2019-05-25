#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import copy

from bes.common import check, string_util
from bes.compat import StringIO
from bes.fs import file_util
from bes.key_value import key_value
from bes.text import text_line_parser
from bes.version.software_version import software_version

class properties(object):
  '''
  A class to manage build properties.  Using either "java" or "yaml" style.

  yaml:
  foo: hi
  bar: 123

  java:
  foo=hi
  bar=123
  '''

  def __init__(self, properties = None):
    properties = properties or {}
    self._properties = copy.deepcopy(properties)

  def add(self, key, value):
    check.check_string(key)
    check.check_string(value)
    self._properties[key] = value

  @classmethod
  def _check_style(clazz, style):
    if style not in [ 'java', 'yaml' ]:
      raise ValueError('invalid style \"{}\".  should be java or yaml.'.format(style))
    
  def to_text(self, style):
    self._check_style(style)
    buf = StringIO()
    for key, value in sorted(self._properties.items()):
      buf.write(self._key_value_to_str(style, key, value))
      buf.write('\n')
    value = buf.getvalue().strip() + '\n'
    if value == '\n':
      value = ''
    return value
    
  def to_yaml_text(self):
    return self.to_text('yaml')

  def to_java_text(self):
    return self.to_text('java')

  @classmethod 
  def _key_value_to_str(clazz, style, key, value):
    if style == 'yaml':
      return """{key}: {value}""".format(key = key,
                                         value = clazz._value_to_yaml_string(value))
    else:
      return """{key}={value}""".format(key = key,
                                        value = clazz._value_to_java_string(value))
  
  @classmethod 
  def _value_to_yaml_string(clazz, value):
    if clazz._value_is_number(value):
      return string_util.quote(value)
    return value

  @classmethod 
  def _value_to_java_string(clazz, value):
    return value
  
  @classmethod 
  def _value_is_number(clazz, value):
    try:
      float(value)
      return True
    except:
      return False

  def save(self, style, filename):
    self._check_style(style)
    file_util.save(filename, content = self.to_text(style))

  def save_to_yaml_file(self, filename):
    self.save('yaml', filename)

  def save_to_java_file(self, filename):
    self.save('java', filename)

  def has_value(self, key):
    return key in self._properties

  def set_value(self, key, value):
    self._properties[key] = value

  def get_value(self, key):
    return self._properties[key]

  def remove_value(self, key):
    del self._properties[key]

  def items(self):
    return items(self._properties.items())

  def keys(self):
    return sorted(self._properties.keys())

  def properties(self):
    return copy.deepcopy(self._properties)

  MAJOR = software_version.MAJOR
  MINOR = software_version.MINOR
  REVISION = software_version.REVISION
  def bump_version(self, key, component, default_value = None, reset_lower = False):
    if not self.has_value(key):
      self.set_value(key, default_value or '1.0.0')
      return
    old_version = self.get_value(key)
    new_version = software_version.bump_version(old_version, component, reset_lower = reset_lower)
    self.set_value(key, new_version)

  def change_version(self, key, component, value):
    if not self.has_value(key):
      self.set_value(key, default_value or '1.0.0')
      return
    old_version = self.get_value(key)
    new_version = software_version.change_component(old_version, component, value)
    self.set_value(key, new_version)
    
  @classmethod
  def _parse_text(clazz, text, filename, delimiter):
    check.check_string(text)
    lines = text_line_parser.parse_lines(text, strip_comments = True, strip_text = True, remove_empties = True)
    result = {}
    for line in lines:
      kv = key_value.parse(line, delimiter = delimiter)
      result[kv.key] = string_util.unquote(kv.value)
    return result

  @classmethod
  def from_text(clazz, style, text, filename):
    clazz._check_style(style)
    check.check_string(text)
    if not text:
      return properties()
    if style == 'yaml':
      delimiter = ':'
    else:
      delimiter = '='
    doc = clazz._parse_text(text, filename, delimiter)
    if not check.is_dict(doc):
      raise ValueError('not a yaml properties file: %s' % (filename))
    return properties(properties = doc)
  
  @classmethod
  def from_yaml_text(clazz, text, filename):
    return clazz.from_text('yaml', text, filename)

  @classmethod
  def from_java_text(clazz, text, filename):
    return clazz.from_text('java', text, filename)

  @classmethod
  def load(clazz, style, filename):
    text = file_util.read(filename, codec = 'utf-8')
    return clazz.from_text(style, text, filename)
  
  @classmethod
  def load_from_yaml_file(clazz, filename):
    assert False
    return clazz.load('yaml', filename)

  @classmethod
  def load_from_java_file(clazz, filename):
    return clazz.load('java', filename)
  
