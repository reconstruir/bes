#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import copy

from bes.common import check, string_util
from bes.compat.ConfigParser import ConfigParser, SafeConfigParser, NoOptionError
from bes.compat import StringIO
from bes.fs import file_util
from bes.key_value import key_value
from bes.text import text_line_parser
from bes.version.version_compare import version_compare
from bes.system import log

class config(object):
  '''
  A class to manage ini style config files.  Uses SafeConfigParser underneath.

  [default]
  color = red
  fruit = apple

  [new_zealand]
  color = green
  fruit = kiwi

  [indonesia]
  color = yellow
  fruit = durian

  [antartica]
  '''

  class Parser(SafeConfigParser):
    def to_dict(self):
      d = dict(self._sections)
      for k in d:
        d[k] = dict(self._defaults, **d[k])
        d[k].pop('__name__', None)
      return copy.deepcopy(d)
  
  def __init__(self, parser = None):
    parser = parser or ConfigParser()
    if not isinstance(parser, ( ConfigParser, SafeConfigParser )):
      raise TypeError('parser should be an instance of ConfigParser or SafeConfigParser.')
    self._parser = parser

  def __str__(self):
    buf = StringIO()
    self._parser.write(buf)
    return buf.getvalue().strip() + '\n'
    
  def set_value(self, section, key, value):
    check.check_string(section)
    check.check_string(key)
    check.check_string(value)
    if not self._parser.has_section(section):
      self._parser.add_section(section)
    self._parser.set(section, key, value)

  def get_value(self, section, key):
    check.check_string(section)
    check.check_string(key)
    if not self._parser.has_section(section):
      raise ValueError('no such section: {}'.format(section))
    try:
      return self._parser.get(section, key)
    except NoOptionError as ex:
      raise ValueError('no such value in section {}: {}'.format(section, key))

  def has_value(self, section, key):
    check.check_string(section)
    check.check_string(key)
    return self._parser.has_option(section, key)
  
  def save(self, filename, codec = None):
    file_util.save(filename, content = str(self), codec = codec)

  MAJOR = version_compare.MAJOR
  MINOR = version_compare.MINOR
  REVISION = version_compare.REVISION
  def bump_version(self, section, key, component = None, default_value = None):
    if not self.has_value(section, key):
      self.set_value(section, key, default_value or '1.0.0')
      return
    old_version = self.get_value(section, key)
    new_version = version_compare.bump_version(old_version, component = component, delimiter = '.')
    self.set_value(section, key, new_version)

#  def change_version(clazz, section, key, component, value, delimiter = '.'):
    
  @classmethod
  def load_from_text(clazz, text, filename):
    parser = clazz._make_parser_from_text(text)
    return config(parser = parser)
  
  @classmethod
  def load_from_file(clazz, filename):
    parser = clazz._make_parser_from_file(filename)
    return config(parser = parser)
  
  @classmethod
  def _make_parser_from_file(clazz, filename, codec = None):
    text = file_util.read(filename, codec = 'utf-8')
    return clazz._make_parser_from_text(text)

  @classmethod
  def _make_parser_from_text(clazz, text):
    parser = clazz.Parser()
    stream = StringIO(text)
    parser.readfp(stream)
    return parser
  
