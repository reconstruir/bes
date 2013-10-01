#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json, unittest
from ObjectUtil import ObjectUtil
from collections import namedtuple

class JsonUtil(object):
  'Json util'

  @classmethod
  def can_encode(clazz, o):
    'Return true if the given object can be encoded as json.'
    try:
      clazz.to_json(o)
      return True
    except Exception, ex:
      return False

  @classmethod
  def to_json(clazz, o, indent = None):
    def default(o):
      if isinstance(o, ObjectUtil.Base__):
        return dict(o.__dict__)
      return json.JSONEncoder.default(self, o)

    return json.dumps(o, indent = indent, default = default)

  @classmethod
  def normalize(clazz, o):
    return json.loads(JsonUtil.to_json(o))

class TestJsonUtil(unittest.TestCase):

  MyClass1 = namedtuple('MyClass1', [ 'foo', 'bar' ])

  class MyClass2(object):
    def __init__(self, x): self._x = x

  def test_can_encode(self):
    self.assertTrue( JsonUtil.can_encode({'a': 5, 'b': 'hi'}) )

    self.assertTrue( JsonUtil.can_encode({'a': 5, 'b': self.MyClass1(6, 'hi')}) )

    self.assertFalse( JsonUtil.can_encode({'a': 5, 'b': self.MyClass2(5)}) )

    i2 = ObjectUtil.make('MyClass3', { 'a': 5, 'b': 'hi' })

    self.assertTrue( JsonUtil.can_encode({'a': 5, 'b': i2}) )

  def test_to_json(self):
    self.assertEqual( '{"a": 5, "b": "hi"}', JsonUtil.to_json(ObjectUtil.make('MyClass4', { 'a': 5, 'b': 'hi' })) )

if __name__ == "__main__":
  unittest.main()
