#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.factory.class_registry import class_registry
from bes.factory.singleton_class_registry import singleton_class_registry
from bes.system.check import check
from bes.testing.unit_test import unit_test

class _fruit_registry(singleton_class_registry):
  __registry_class_name_prefix__ = 'fruit_'
  __registry_raise_on_existing__ = True


class _fruit_register(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != '_fruit_base':
      _fruit_registry.register(clazz)
    return clazz

class _fruit_base(object, metaclass = _fruit_register):

  @classmethod
  @abstractmethod
  def name(clazz):
    'Return name for this fruit.'
    raise NotImplementedError('name')
  
  @abstractmethod
  def price(self):
    'Price for this fruit.'
    raise NotImplementedError('price')
  
check.register_class(_fruit_base, name = 'face_detector_engine', include_seq = False)

class fruit_apple(_fruit_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    return 'apple'
  
  #@abstractmethod
  def price(self):
    return 666

class fruit_kiwi(_fruit_base):

  @classmethod
  #@abstractmethod
  def name(clazz):
    return 'kiwi'
  
  #@abstractmethod
  def price(self):
    return 42
  
class test_class_registry(unit_test):
  
  def test_registry(self):
    self.assertEqual( {
      'fruit_apple': fruit_apple,
      'fruit_kiwi': fruit_kiwi,
      }, _fruit_registry.registry() )

  def test_keys(self):
    self.assertEqual( [
      'fruit_apple',
      'fruit_kiwi',
    ], _fruit_registry.keys() )

  def test_shortcut_keys(self):
    self.assertEqual( [
      'apple',
      'kiwi',
    ], _fruit_registry.shortcut_keys() )
    
  def test_get(self):
    self.assertEqual( fruit_apple, _fruit_registry.get('fruit_apple') )
    self.assertEqual( fruit_apple, _fruit_registry.get('apple') )

  def test_make(self):
    self.assertEqual( 'apple', _fruit_registry.make('fruit_apple').name() )
    self.assertEqual( 666, _fruit_registry.make('fruit_apple').price() )
    self.assertEqual( 'apple', _fruit_registry.make('apple').name() )
    self.assertEqual( 666, _fruit_registry.make('apple').price() )
    self.assertEqual( 'kiwi', _fruit_registry.make('fruit_kiwi').name() )
    self.assertEqual( 42, _fruit_registry.make('fruit_kiwi').price() )
    self.assertEqual( 'kiwi', _fruit_registry.make('kiwi').name() )
    self.assertEqual( 42, _fruit_registry.make('kiwi').price() )

  def test_values(self):
    self.assertEqual( [
      fruit_apple,
      fruit_kiwi,
    ], _fruit_registry.values() )
    
if __name__ == '__main__':
  unit_test.main()
