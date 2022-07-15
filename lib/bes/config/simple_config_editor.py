#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from ..system.check import check
from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util

from .simple_config import simple_config
from .simple_config_options import simple_config_options

class simple_config_editor(object):
  'A class to manipulate simple config files'

  def __init__(self, filename, options = None):
    check.check_string(filename)
    check.check_simple_config_options(options, allow_none = True)

    self._options = options or simple_config_options()
    self._filename = path.abspath(filename)
    if not path.isfile(self._filename):
      file_util.save(self._filename, content = '')

  def __str__(self):
    return str(self._config)
      
  def set_value(self, section_name, key, value):
    check.check_string(section_name)
    check.check_string(key)
    check.check_string(value)
    
    self._config.set_value(section_name, key, value)
    self._config.save(self._filename)
    assert path.isfile(self._filename)

  def set_values(self, section_name, values):
    check.check_string(section_name)
    
    self._config.set_values(section_name, values)
    self._config.save(self._filename)
    assert path.isfile(self._filename)
    
  def has_value(self, section_name, key):
    check.check_string(section_name)
    check.check_string(key)
    
    return self._config.has_value(section_name, key)

  def get_value(self, section_name, key):
    check.check_string(section_name)
    check.check_string(key)

    self._check_file_exists()
    self._check_key(section_name, key)
    return self._config.get_value(section_name, key)

  def get_value_with_default(self, section_name, key, default):
    check.check_string(section_name)
    check.check_string(key)
    check.check_string(default, allow_none = True)

    self._check_file_exists()
    return self._config.get_value_with_default(section_name, key, default)
  
  def get_values(self, section_name):
    check.check_string(section_name)
    
    self._check_file_exists()
    return self._config.get_values(section_name)

  def has_section(self, section_name):
    check.check_string(section_name)
    
    return self._config.has_section(section_name)

  def sections(self):
    return self._config.sections()

  def _check_file_exists(self):
    if not path.exists(self._filename):
      raise IOError('config file not found: {}'.format(self._filename))

  def _check_key(self, section_name, key):
    if not self.has_value(section_name, key):
      raise KeyError('value \"{}\" in section {} not found in {}'.format(key, section_name, self._filename))

  def import_file(self, filename):
    other_config = simple_config.from_file(filename, options = self._options)
    for section in other_config:
      other_values = section.to_dict()
      for key, value in other_values.items():
        self.set_value(section.header_.name, key, value)
    
  @cached_property
  def _config(self):
    if self._filename:
      if not path.isfile(self._filename):
        raise IOError('config file not found: {}'.format(self._filename))
      return simple_config.from_file(self._filename, options = self._options)
    else:
      return simple_config(source = '<simple_config_editor>')

  @property
  def filename(self):
    return self._filename
    
check.register_class(simple_config_editor, include_seq = False)
