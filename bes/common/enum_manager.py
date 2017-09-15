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
  
  
'''
class _enum_meta_class(type):
  'Cheesy enum.  Id rather use the one in python3 but i want to support python 2.7 with no exta deps.'
  
  def __new__(meta, name, bases, class_dict):
    clazz = type.__new__(meta, name, bases, class_dict)
    if clazz.__name__ != 'enum':
      names = [ f for f in clazz.__dict__ if not f.startswith('_') ]
      names = [ f for f in names if f not in [ 'DEFAULT' ] ]
      values = [ getattr(clazz, name) for name in names ]

      for value in values:
        if not isinstance(value, int):
          raise TypeError('Value should be of type int instead of %s: %s' % (type(value), str(value)))

      names_values = zip(names, values)
      setattr(clazz, '_NAME_VALUES', sorted(names_values))
      setattr(clazz, '_NAMES', sorted(names))
      setattr(clazz, '_VALUES', sorted(values))
      
      name_to_value = {}
      min_value = None
      value_to_name = {}
      for name in names:
        value = getattr(clazz, name)
        name_to_value[name] = getattr(clazz, name)
        if min_value is None:
          min_value = value
        else:
          min_value = min(min_value, value)
        if not value_to_name.has_key(value):
          value_to_name[value] = []
        value_to_name[value].append(name)
          
      setattr(clazz, '_NAME_TO_VALUE', name_to_value)
      setattr(clazz, '_VALUE_TO_NAME', value_to_name)

      if not hasattr(clazz, 'DEFAULT'):
        setattr(clazz, 'DEFAULT', min_value)
      default = getattr(clazz, 'DEFAULT')
      if not isinstance(default, int):
        raise TypeError('DEFAULT should be of type int instead of %s: %s' % (type(default), str(default)))
      if not default in values:
        raise ValueError('DEFAULT invalid: %d' % (default))
      
    return clazz

class enum(object):

  __metaclass__ = _enum_meta_class

  def __init__(self, value = None):
    if value is None:
      value = self.DEFAULT
    self.assign(value)

  def __str__(self):
    return self._VALUE_TO_NAME[self._value][0]
    
  @classmethod
  def value_is_valid(clazz, value):
    return value in clazz._VALUES

  @classmethod
  def name_is_valid(clazz, name):
    return name in clazz._NAMES

  def assign(self, something):
    if isinstance(something, self.__class__):
      self.value = something.value
    elif isinstance(something, ( str, unicode )):
      self.value = self.parse(something)
    elif isinstance(something, int):
      self.value = something
    else:
      raise ValueError('invalid value: %s' % (str(something)))
  
  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    if not self.value_is_valid(value):
      raise ValueError('Invalid value: %s - should be one of %s' % (value, self._make_choices_blurb()))
    self._value = value

  @property
  def name(self):
    return self._VALUE_TO_NAME[self._value][0]

  @name.setter
  def name(self, name):
    if not self.name_is_valid(name):
      raise ValueError('Invalid name: %s - should be one of %s' % (name, self._make_choices_blurb()))
    self.value = self._NAME_TO_VALUE[name]

  @classmethod
  def _make_choices_blurb(clazz):
    return ' '.join([ '%s(%s)' % (name, value) for name, value in clazz._NAME_VALUES ])
    
  @classmethod
  def parse(clazz, s):
    if not isinstance(s, basestring):
      raise TypeError('Value to parse should be a string instead of: %s - %s' % (str(s), type(s)))
    if not s in clazz._NAMES:
      raise ValueError('Value invalid: %s' % (str(s)))
    return clazz._NAME_TO_VALUE[s]
'''
