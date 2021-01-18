#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from bes.common.check import check
from bes.common.string_util import string_util
from bes.compat.StringIO import StringIO
from bes.fs.file_util import file_util
from bes.key_value.key_value import key_value
from bes.system.log import logger
from bes.text.text_line_parser import text_line_parser
from bes.text.comments import comments
from bes.version.software_version import software_version

from .properties_file_formatter_plain import properties_file_formatter_plain
from .properties_file_formatter_java import properties_file_formatter_java
from .properties_file_formatter_yaml import properties_file_formatter_yaml

class properties(object):
  '''
  A class to manage properties.  Inspired by java properties files.
  A formatter interface can be used to control how the class 
  formats values.
  '''

  logger = logger('properties')
  
  _FORMATTER_JAVA = properties_file_formatter_java()
  _FORMATTER_YAML = properties_file_formatter_yaml()
  
  def __init__(self, values = None):
    values = values or {}
    check.check_dict(values, check.STRING_TYPES)
    
    self._values = copy.deepcopy(values)

  def add(self, key, value):
    check.check_string(key)
    check.check_string(value)
    
    self._values[key] = value

  def to_text(self, formatter):
    buf = StringIO()
    for key, value in sorted(self.values().items()):
      formatted_value = formatter.value_to_text(key, value)
      formatted_key_value = formatter.key_value_to_text(key, formatted_value)
      buf.write(formatted_key_value)
      buf.write('\n')
    result = buf.getvalue().strip()
    result = result + '\n'
    if result == '\n':
      result = ''
    return result
    
  def to_yaml_text(self):
    return self.to_text(self._FORMATTER_YAML)

  def to_java_text(self):
    return self.to_text(self._FORMATTER_JAVA)

  def save(self, filename, formatter):
    file_util.save(filename, content = self.to_text(formatter))

  def save_to_yaml_file(self, filename):
    self.save(filename, self._FORMATTER_YAML)

  def save_to_java_file(self, filename):
    self.save(filename, self._FORMATTER_JAVA)
    
  def has_value(self, key):
    return key in self._values

  def set_value(self, key, value):
    self._values[key] = value

  def get_value(self, key):
    return self._values[key]

  def remove_value(self, key):
    del self._values[key]

  def items(self):
    return sorted(self._values.items())

  def keys(self):
    return sorted(self._values.keys())

  def values(self):
    return copy.deepcopy(self._values)

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
  def _parse_text(clazz, text, filename, formatter):
    parser = text_line_parser(text)
    result = {}
    for line in parser:
      text = comments.strip_line(line.text, allow_quoted = False).strip()
      if text:
        clazz.logger.log_d('_parse_text: line=|{}|'.format(text))
        left, delimiter, right = text.partition(formatter.delimiter())
        if delimiter != formatter.delimiter():
          raise ValueError('invalid property file syntax at {}:{} - "{}"'.format(filename,
                                                                                 line.line_number,
                                                                                 text))
        key = left.strip()
        value = formatter.parse_value(key, right.strip())
        clazz.logger.log_d('_parse_text: key={} value=|{}|'.format(key, value))
        result[key] = value
    return result

  @classmethod
  def from_text(clazz, text, filename, formatter):
    check.check_string(text)
    check.check_string(filename)
    check.check_properties_file_formatter(formatter)

    if not text:
      return properties()
    values = clazz._parse_text(text, filename, formatter)
    if not check.is_dict(values):
      raise ValueError('not a properties file: "{}"'.format(filename))
    return properties(values = values)
  
  @classmethod
  def from_yaml_text(clazz, text, filename):
    return clazz.from_text(text, filename, clazz._FORMATTER_YAML)

  @classmethod
  def from_java_text(clazz, text, filename):
    return clazz.from_text(text, filename, clazz._FORMATTER_JAVA)
  
  @classmethod
  def load(clazz, filename, formatter):
    text = file_util.read(filename, codec = 'utf-8')
    return clazz.from_text(text, filename, formatter)
  
  @classmethod
  def load_from_yaml_file(clazz, filename):
    return clazz.load(filename, clazz._FORMATTER_YAML)

  @classmethod
  def load_from_java_file(clazz, filename):
    return clazz.load(filename, clazz._FORMATTER_JAVA)
