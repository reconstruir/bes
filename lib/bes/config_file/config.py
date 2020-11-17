#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import copy

from bes.common.check import check
from bes.common.string_util import string_util
from bes.compat.ConfigParser import ConfigParser
from bes.compat.ConfigParser import NoOptionError
from bes.compat.ConfigParser import SafeConfigParser
from bes.compat.StringIO import StringIO
from bes.fs.file_util import file_util
from bes.key_value.key_value import key_value
from bes.system.compat import compat
from bes.system.log import log
from bes.text.text_line_parser import text_line_parser
from bes.version.software_version import software_version
from bes.system.compat import compat

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

  _DEFAULT_SECTION = 'default'

  class Parser(SafeConfigParser):

    def __init__(self, *args, **kargs):
      # Python 3 breaks compatibility with SafeConfigParser by making the
      # inline_comment_prefixes be None instead of ';' which is a
      # ridiculous breakage but nevertheless it happened so deal with it.
      if compat.IS_PYTHON3:
        kargs = copy.deepcopy(kargs)
        kargs['comment_prefixes'] = ('#', ';')
        kargs['inline_comment_prefixes'] = (';', )
      SafeConfigParser.__init__(self, *args, **kargs)
    
    def to_dict(self):
      d = dict(self._sections)
      for k in d:
        d[k] = dict(self._defaults, **d[k])
        d[k].pop('__name__', None)
      return copy.deepcopy(d)
  
  def __init__(self, parser = None, string_quote_char = None):
    check.check_string(string_quote_char, allow_none = True)
    
    if string_quote_char:
      assert string_quote_char in [ '"', "'" ]

    parser = parser or self.Parser()
    if not isinstance(parser, ( ConfigParser, SafeConfigParser )):
      raise TypeError('parser should be an instance of ConfigParser or SafeConfigParser.')
    self._parser = parser
    self._string_quote_char = string_quote_char

  def __str__(self):
    buf = StringIO()
#    for section in self._parser.sections():
#      for x in self._parser.items(section):
#        print('HI: {} x={}'.format(section, x))
#    assert False
    self._parser.write(buf)
    return buf.getvalue().strip() + '\n'

  def _value_for_set(self, value):
    if self._string_quote_char:
      return string_util.quote(value, quote_char = self._string_quote_char)
    return value

  def _value_for_get(self, value):
    if self._string_quote_char:
      return string_util.unquote(value)
    return value

  def has_section(self, section):
    check.check_string(section)
    
    return self._parser.has_section(section)
  
  def set_value(self, section, key, value):
    check.check_string(section)
    check.check_string(key)
    check.check_string(value)
    if not self._parser.has_section(section):
      self._parser.add_section(section)
    self._parser.set(section, key, self._value_for_set(value))

  def set_values(self, section, values):
    check.check_string(section)
    check.check_dict(values, check.STRING_TYPES, check.STRING_TYPES)
    if not self._parser.has_section(section):
      self._parser.add_section(section)
    for key, value in sorted(values.items()):
      self._parser.set(section, key, self._value_for_set(value))

  def update_config(self, values_dict):
    check.check_dict(values_dict, check.STRING_TYPES, dict)

    for _, section_values in values_dict.items():
      check.check_dict(section_values, check.STRING_TYPES, check.STRING_TYPES)
      
    for section, section_values in values_dict.items():
      self.set_values(section, section_values)
      
  def get_value(self, section, key):
    check.check_string(section)
    check.check_string(key)
    
    if not self._parser.has_section(section):
      raise ValueError('no such section: {}'.format(section))

    if self._parser.has_option(section, key):
      return self._value_for_get(self._parser.get(section, key))

    if self._parser.has_option(self._DEFAULT_SECTION, key):
      return self._value_for_get(self._parser.get(self._DEFAULT_SECTION, key))
    
    raise ValueError('no such value in section {}: {}'.format(section, key))

  def has_default_section(self):
    return self.has_section(self._DEFAULT_SECTION)
  
  def get_values(self, section):
    check.check_string(section)
    
    if not self._parser.has_section(section):
      raise ValueError('no such section: {}'.format(section))

    result = {}
    if self.has_default_section():
      default_values = self._get_values_for_section(self._DEFAULT_SECTION)
      for key, value in default_values.items():
        result[key] = self._value_for_get(value) 
      
    values = self._get_values_for_section(section)
    for key, value in values.items():
      result[key] = self._value_for_get(value) 
    return result

  def _get_values_for_section(self, section):
    result = {}
    for key, value in dict(self._parser.items(section)).items():
      result[key] = self._value_for_get(value) 
    return result
  
  def has_value(self, section, key):
    check.check_string(section)
    check.check_string(key)
    
    if self._parser.has_option(section, key):
      return True
    if self.has_default_section():
      return self._parser.has_option(self._DEFAULT_SECTION, key)
    return False
  
  def save(self, filename, codec = 'utf-8'):
    file_util.save(filename, content = str(self), codec = codec)

  MAJOR = software_version.MAJOR
  MINOR = software_version.MINOR
  REVISION = software_version.REVISION
  def bump_version(self, section, key, component, default_value = None, reset_lower = False):
    if not self.has_value(section, key):
      self.set_value(section, key, default_value or '1.0.0')
      return
    old_version = self.get_value(section, key)
    new_version = software_version.bump_version(old_version, component, reset_lower = reset_lower)
    self.set_value(section, key, new_version)

  def change_version(self, section, key, component, value):
    if not self.has_value(section, key):
      self.set_value(key, default_value or '1.0.0')
      return
    old_version = self.get_value(section, key)
    new_version = software_version.change_component(old_version, component, value)
    self.set_value(section, key, new_version)

  def sections(self):
    return self._parser.sections()

  def to_dict(self):
    result = {}
    for section in self.sections():
      result[section] = self.get_values(section)
    return result

  def _reset(self):
    for section in self._parser.sections():
      for key, value in self._parser.items(section):
        self._parser.set(section, key, self._value_for_set(value))
  
  @classmethod
  def load_from_text(clazz, text, filename, string_quote_char = None):
    parser = clazz._make_parser_from_text(text)
    cfg = config(parser = parser, string_quote_char = string_quote_char)
    if string_quote_char:
      cfg._reset()

    return cfg
  
  @classmethod
  def load_from_file(clazz, filename, string_quote_char = None):
    parser = clazz._make_parser_from_file(filename)
    cfg = config(parser = parser, string_quote_char = string_quote_char)
    if string_quote_char:
      cfg._reset()
    return cfg
  
  @classmethod
  def _make_parser_from_file(clazz, filename, codec = 'utf-8'):
    text = file_util.read(filename, codec = codec)
    return clazz._make_parser_from_text(text)

  @classmethod
  def _make_parser_from_text(clazz, text):
    parser = clazz.Parser()
    stream = StringIO(text)
    if compat.IS_PYTHON3:
      parser.read_file(stream)
    else:
      parser.readfp(stream)
    return parser
