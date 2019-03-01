#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.common import check

from .properties import properties

class properties_editor(object):
  '''
  A class to manipulate a yaml properties file.
  '''

  def __init__(self, filename):
    check.check_string(filename)
    self._filename = path.abspath(filename)
    
  def set_value(self, key, value):
    check.check_string(key)
    check.check_string(value)
    props = self._load_or_initialize()
    props.set_value(key, value)
    props.save_to_yaml_file(self._filename)
    assert path.isfile(self._filename)

  def get_value(self, key):
    check.check_string(key)
    self._check_file_exists()
    props = properties.load_from_yaml_file(self._filename)
    self._check_key(props, key)
    return props.get_value(key)

  def remove_value(self, key):
    check.check_string(key)
    self._check_file_exists()
    props = properties.load_from_yaml_file(self._filename)
    self._check_key(props, key)
    props.remove_value(key)
    props.save_to_yaml_file(self._filename)

  def keys(self):
    self._check_file_exists()
    props = properties.load_from_yaml_file(self._filename)
    return props.keys()

  def bump_version(self, key, component = None):
    check.check_string(key)
    props = self._load_or_initialize()
    props.bump_version(key, component = component)
    props.save_to_yaml_file(self._filename)

  def properties(self):
    check.check_string(key)
    self._check_file_exists()
    props = properties.load_from_yaml_file(self._filename)
    return props.properties()
    
  def _check_file_exists(self):
    if not path.exists(self._filename):
      raise IOError('properties file not found: %s' % (self._filename))

  def _check_key(self, props, key):
    if not props.has_value(key):
      raise KeyError('property \"%s\" not found in %s' % (key, self._filename))

  def _load_or_initialize(self):
    if path.exists(self._filename):
      return properties.load_from_yaml_file(self._filename)
    else:
      return properties()
