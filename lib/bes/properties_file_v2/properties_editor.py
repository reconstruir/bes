#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from ..system.check import check
from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from .properties import properties

class properties_editor(object):
  '''
  A class to manipulate a properties file
  '''

  def __init__(self, filename, formatter = None, backup = False):
    check.check_string(filename)
    check.check_properties_file_formatter(formatter, allow_none = True)
    check.check_bool(backup)
    
    self.filename = path.abspath(filename)
    self._formatter = formatter or properties._FORMATTER_YAML
    self._backup = backup
    if not path.isfile(self.filename):
      file_util.save(self.filename, content = '')
    
  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)
    
    self._properties.set_value(key, value)
    result = self._save()
    assert path.isfile(self.filename)
    return result

  def has_value(self, key):
    return self._properties.has_value(key)

  def get_value(self, key):
    check.check_string(key)
    
    self._check_file_exists()
    self._check_key(key)
    return self._properties.get_value(key)

  def get_value_with_default(self, key, default_value):
    check.check_string(key)
    
    self._check_file_exists()
    return self._properties.get_value_with_default(key, default_value)
  
  def remove_value(self, key):
    check.check_string(key)
    
    self._check_file_exists()
    self._check_key(key)
    self._properties.remove_value(key)
    return self._save()

  def keys(self):
    self._check_file_exists()
    return self._properties.keys()

  def values(self):
    self._check_file_exists()
    return self._properties.values()

  def items(self):
    self._check_file_exists()
    return self._properties.items()
  
  def bump_version(self, key, component, reset_lower = False):
    check.check_string(key)
    self._properties.bump_version(key, component, reset_lower = reset_lower)
    return self._save()

  def change_version(self, key, component, value):
    check.check_string(key)
    
    self._properties.change_version(key, component, value)
    return self._save()
    
  def values(self):
    self._check_file_exists()
    return self._properties.values()
    
  def _check_file_exists(self):
    if not path.exists(self.filename):
      raise IOError('properties file not found: %s' % (self.filename))

  def _check_key(self, key):
    if not self.has_value(key):
      raise KeyError('property \"%s\" not found in %s' % (key, self.filename))

  @cached_property
  def _properties(self):
    if self.filename:
      if not path.isfile(self.filename):
        raise IOError('properties file not found: %s' % (self.filename))
      return properties.load(self.filename, self._formatter)
    else:
      return properties()

  def _save(self):
    if path.exists(self.filename):
      old_checksum = file_util.checksum('sha256', self.filename)
    else:
      old_checksum = None
    tmp_file = temp_file.make_temp_file()
    self._properties.save(tmp_file, self._formatter)
    new_checksum = file_util.checksum('sha256', tmp_file)
    if old_checksum == new_checksum:
      return False
    if self._backup and not file_util.is_empty(self.filename):
      file_util.backup(self.filename)
    file_util.copy(tmp_file, self.filename)
    return True
