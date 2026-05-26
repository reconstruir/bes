#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.files.media_finder.bf_media_attr_resolver_base import bf_media_attr_resolver_base
from bes.files.media_finder.bf_media_attr_resolver_registry import bf_media_attr_resolver_registry

class _FakeResolverA(bf_media_attr_resolver_base):
  name = '_test_fake_a'
  @classmethod
  def resolve(cls, filename, mime_type, attr_name):
    return None

class _FakeResolverB(bf_media_attr_resolver_base):
  name = '_test_fake_b'
  @classmethod
  def resolve(cls, filename, mime_type, attr_name):
    return None

class _FakeResolverC(bf_media_attr_resolver_base):
  name = '_test_fake_c'
  @classmethod
  def resolve(cls, filename, mime_type, attr_name):
    return 42

class test_bf_media_attr_resolver_registry(unit_test):

  def setUp(self):
    # Isolate each test by saving and restoring registry state
    self._orig = dict(bf_media_attr_resolver_registry._registry)

  def tearDown(self):
    bf_media_attr_resolver_registry._registry.clear()
    bf_media_attr_resolver_registry._registry.update(self._orig)

  def test_register_and_get(self):
    bf_media_attr_resolver_registry.register(_FakeResolverA)
    self.assertIs(_FakeResolverA, bf_media_attr_resolver_registry.get('_test_fake_a'))

  def test_get_unknown_raises(self):
    with self.assertRaises(KeyError):
      bf_media_attr_resolver_registry.get('_no_such_resolver')

  def test_names_contains_registered(self):
    bf_media_attr_resolver_registry.register(_FakeResolverA)
    self.assertIn('_test_fake_a', bf_media_attr_resolver_registry.names())

  def test_register_two_resolvers(self):
    bf_media_attr_resolver_registry.register(_FakeResolverA)
    bf_media_attr_resolver_registry.register(_FakeResolverB)
    self.assertIs(_FakeResolverA, bf_media_attr_resolver_registry.get('_test_fake_a'))
    self.assertIs(_FakeResolverB, bf_media_attr_resolver_registry.get('_test_fake_b'))

  def test_register_overwrites_same_name(self):
    bf_media_attr_resolver_registry.register(_FakeResolverA)
    bf_media_attr_resolver_registry.register(_FakeResolverC)
    # _FakeResolverC also has name '_test_fake_c', not overlapping; test explicit overwrite
    class _Override(bf_media_attr_resolver_base):
      name = '_test_fake_a'
      @classmethod
      def resolve(cls, filename, mime_type, attr_name):
        return 'overridden'
    bf_media_attr_resolver_registry.register(_Override)
    self.assertIs(_Override, bf_media_attr_resolver_registry.get('_test_fake_a'))

  def test_names_returns_list(self):
    bf_media_attr_resolver_registry.register(_FakeResolverA)
    result = bf_media_attr_resolver_registry.names()
    self.assertIsInstance(result, list)

if __name__ == '__main__':
  unit_test.main()
