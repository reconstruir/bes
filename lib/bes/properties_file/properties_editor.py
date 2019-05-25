#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.common import check
from bes.property.cached_property import cached_property
from bes.fs import file_util

from .properties import properties

class properties_editor(object):
  '''
  A class to manipulate a yaml or java properties file.
  '''

  def __init__(self, filename, style = None):
    style = style or 'yaml'
    check.check_string(filename)
    self._style = style
    self._filename = path.abspath(filename)
    if not path.isfile(self._filename):
      file_util.save(self._filename, content = '')
    
  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)
    self._properties.set_value(key, value)
    self._properties.save(self._style, self._filename)
    assert path.isfile(self._filename)

  def has_value(self, key):
    return self._properties.has_value(key)

  def get_value(self, key):
    check.check_string(key)
    self._check_file_exists()
    self._check_key(key)
    return self._properties.get_value(key)

  def remove_value(self, key):
    check.check_string(key)
    self._check_file_exists()
    self._check_key(key)
    self._properties.remove_value(key)
    self._properties.save(self._style, self._filename)

  def keys(self):
    self._check_file_exists()
    return self._properties.keys()

  def bump_version(self, key, component, reset_lower = False):
    check.check_string(key)
    self._properties.bump_version(key, component, reset_lower = reset_lower)
    self._properties.save(self._style, self._filename)

  def change_version(self, key, component, value):
    check.check_string(key)
    self._properties.change_version(key, component, value)
    self._properties.save(self._style, self._filename)
    
  def properties(self):
    self._check_file_exists()
    return self._properties.properties()
    
  def _check_file_exists(self):
    if not path.exists(self._filename):
      raise IOError('properties file not found: %s' % (self._filename))

  def _check_key(self, key):
    if not self.has_value(key):
      raise KeyError('property \"%s\" not found in %s' % (key, self._filename))

  @cached_property
  def _properties(self):
    if self._filename:
      if not path.isfile(self._filename):
        raise IOError('properties file not found: %s' % (self._filename))
      return properties.load(self._style, self._filename)
    else:
      return properties()
