#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class enum_manager(object):

  _name_value = namedtuple('_name_value', 'name,value')
  
  def __init__(self):
    self._default_value = None
    self._values = []
    self._names = []
    self._name_values = []
    self._name_to_value = {}
    self._value_to_name = {}

  @property
  def name_values(self):
    return self._name_values

  def add_value(self, name, value):
    if not isinstance(name, basestring):
      raise TypeError('name should be an string instead of: %s - %s' % (str(name), type(name)))
    if not isinstance(value, int):
      raise TypeError('value should be an int instead of: %s - %s' % (str(value), type(value)))

    duplicate_name = name in self._names
    duplicate_value = value in self._values

    self._values.append(value)
    self._names.append(name)
    self._name_values.append(self._name_value(name, value))
    self._name_to_value[name] = value
    if not duplicate_value:
      self._value_to_name[value] = name
    
  @property
  def default_value(self):
    return self._default_value

  @property
  def has_default_value(self):
    return self._default_value != None

  @default_value.setter
  def default_value(self, default_value):
    if default_value is None:
      self._default_value = None
      return
    if not self.value_is_valid(default_value):
      raise ValueError('Invalid value: %s - should be one of %s' % (default_value, self._make_choices_blurb()))
    self._default_value = default_value
    
  def value_is_valid(self, value):
    return value in self._values

  def name_is_valid(self, name):
    return name in self._names

  def _make_choices_blurb(self):
    return ' '.join([ '%s(%s)' % (x.name, x.value) for x in self._name_values ])

  def parse_name(self, name):
    if not isinstance(name, basestring):
      raise TypeError('name to parse should be a string instead of: %s - %s' % (str(name), type(name)))
    if not name in self._names:
      return None
    return self._name_to_value[name]
  
  def value_to_name(self, value):
    self.check_value(value)
    return self._value_to_name[value]
  
  def name_to_value(self, name):
    self.check_name(name)
    return self._name_to_value[name]

  def check_value(self, value):
    if not self.value_is_valid(value):
      raise ValueError('Invalid value: %s - should be one of %s' % (value, self._make_choices_blurb()))
    return value
  
  def check_name(self, name):
    if not self.name_is_valid(name):
      raise ValueError('Invalid name: %s - should be one of %s' % (name, self._make_choices_blurb()))
    return name

  def parse_mask(self, smask, delimiter = '|'):
    if not isinstance(smask, basestring):
      raise TypeError('mask to parse should be a string instead of: %s - %s' % (str(smask), type(smask)))
    names = smask.split(delimiter)
    names = [ n.strip() for n in names if n.strip() ]
    result = 0
    for name in names:
      value = self.parse_name(name)
      if not value:
        return None
      result |= value
    return result
