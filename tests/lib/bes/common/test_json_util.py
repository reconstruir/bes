#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import tempfile, unittest
from collections import namedtuple
from bes.common import json_util, tuple_util

class Testjson_util(unittest.TestCase):

  MyClass1 = namedtuple('MyClass1', [ 'foo', 'bar' ])

  class MyClass2(object):
    def __init__(self, x): self._x = x

  def test_can_encode(self):
    self.assertTrue( json_util.can_encode({'a': 5, 'b': 'hi'}) )

    self.assertTrue( json_util.can_encode({'a': 5, 'b': self.MyClass1(6, 'hi')}) )

    self.assertTrue( json_util.can_encode({'a': 5, 'b': self.MyClass2(5)}) )

    i2 = tuple_util.dict_to_named_tuple('MyClass3', { 'a': 5, 'b': 'hi' })

    self.assertTrue( json_util.can_encode({'a': 5, 'b': i2}) )

  def test_to_json(self):
    self.assertEqual( '[5, "hi"]', json_util.to_json(tuple_util.dict_to_named_tuple('MyClass4', { 'a': 5, 'b': 'hi' })) )

  def test_read_save(self):
    self.assertEqual( '[5, "hi"]', json_util.to_json(tuple_util.dict_to_named_tuple('MyClass4', { 'a': 5, 'b': 'hi' })) )
    expected_object = { 'a': 5, 'b': 'hi' }
    tmp = tempfile.NamedTemporaryFile(mode = 'w')
    json_util.save_file(tmp.name, expected_object, indent = 2)
    actual_object = json_util.read_file(tmp.name)
    self.assertEqual( expected_object, actual_object )
    
if __name__ == "__main__":
  unittest.main()
