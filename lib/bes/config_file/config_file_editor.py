#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util

from .config import config

class config_file_editor(object):
  '''
  A class to manipulate ini style config files
  '''

  def __init__(self, filename, string_quote_char = None):
    check.check_string(filename)
    self._filename = path.abspath(filename)
    self._string_quote_char = string_quote_char
    if not path.isfile(self._filename):
      file_util.save(self._filename, content = '')
    
  def set_value(self, section, key, value):
    check.check_string(section)
    check.check_string(key)
    check.check_string(value)
    self._config.set_value(section, key, value)
    self._config.save(self._filename)
    assert path.isfile(self._filename)

  def set_values(self, section, values):
    check.check_string(section)
    check.check_dict(values, check.STRING_TYPES, check.STRING_TYPES)
    self._config.set_values(section, values)
    self._config.save(self._filename)
    assert path.isfile(self._filename)
    
  def has_value(self, section, key):
    check.check_string(section)
    check.check_string(key)
    return self._config.has_value(section, key)

  def get_value(self, section, key):
    check.check_string(section)
    check.check_string(key)
    self._check_file_exists()
    self._check_key(section, key)
    return self._config.get_value(section, key)

  def get_values(self, section):
    check.check_string(section)
    self._check_file_exists()
    return self._config.get_values(section)

  def bump_version(self, section, key, component, reset_lower = False):
    check.check_string(section)
    check.check_string(key)
    self._config.bump_version(section, key, component, reset_lower = reset_lower)
    self._config.save(self._filename)

  def change_version(self, section, key, component, value):
    check.check_string(section)
    check.check_string(key)
    self._config.change_version(section, key, component, value)
    self._config.save(self._filename)

  def sections(self):
    return self._config.sections()

  def _check_file_exists(self):
    if not path.exists(self._filename):
      raise IOError('config file not found: {}'.format(self._filename))

  def _check_key(self, section, key):
    if not self.has_value(section, key):
      raise KeyError('value \"{}\" in section {} not found in {}'.format(key, section, self._filename))

  @cached_property
  def _config(self):
    if self._filename:
      if not path.isfile(self._filename):
        raise IOError('config file not found: {}'.format(self._filename))
      return config.load_from_file(self._filename, string_quote_char = self._string_quote_char)
    else:
      return config()
