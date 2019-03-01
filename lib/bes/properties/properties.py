#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import copy
#import yaml

from bes.common import check, string_util
from bes.compat import StringIO
from bes.fs import file_util
from bes.key_value import key_value
from bes.text import text_line_parser
from bes.version.version_compare import version_compare

class properties(object):
  '''
  A class to manage build properties.
  '''

  def __init__(self, properties = None):
    properties = properties or {}
    self._properties = copy.deepcopy(properties)

  def add(self, property):
    self._properties.append(property)
    
  def to_yaml_text(self):
    buf = StringIO()
    for key, value in sorted(self._properties.items()):
      buf.write(self._key_value_to_yaml(key, value))
      buf.write('\n')
    value = buf.getvalue().strip() + '\n'
    if value == '\n':
      value = ''
    return value

  @classmethod 
  def _key_value_to_yaml(clazz, key, value):
    return """{key}: '{value}'""".format(key = key, value = value)
  
  def save_to_yaml_file(self, filename):
    content = self.to_yaml_text()
    file_util.save(filename, content = content)

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

  MAJOR = version_compare.MAJOR
  MINOR = version_compare.MINOR
  REVISION = version_compare.REVISION
  def bump_version(self, key, component = None):
    if not self.has_value(key):
      self.set_value(key, '1.0.0')
      return
    old_version = self.get_value(key)
    new_version = version_compare.bump_version(old_version, component = component, delimiter = '.')
    self.set_value(key, new_version)

  @classmethod
  def from_yaml_text(clazz, text, filename):
    check.check_string(text)
    if not text:
      return properties()
    doc = clazz._parse_text(text, filename)
    #doc = yaml.load(text)
    if not check.is_dict(doc):
      raise ValueError('not a yaml properties file: %s' % (filename))
    return properties(properties = doc)

  @classmethod
  def _parse_text(clazz, text, filename):
    check.check_string(text)
    lines = text_line_parser.parse_lines(text, strip_comments = True, strip_text = True, remove_empties = True)
    result = {}
    for line in lines:
      kv = key_value.parse(line, delimiter = ':')
      result[kv.key] = string_util.unquote(kv.value)
    return result
  
  @classmethod
  def load_from_yaml_file(clazz, filename):
    text = file_util.read(filename)
    return clazz.from_yaml_text(text, filename)
