#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import tempfile
from collections import namedtuple

from bes.testing.unit_test import unit_test
from bes.common.json_util import json_util
from bes.common.tuple_util import tuple_util
from bes.system.filesystem import filesystem

class test_json_util(unit_test):

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
    tmp_dir = tempfile.mkdtemp(prefix = 'tead_save', suffix = '.json')
    tmp = path.join(tmp_dir, 'foo.json')
    json_util.save_file(tmp, expected_object, indent = 2)
    actual_object = json_util.read_file(tmp)
    self.assertEqual( expected_object, actual_object )
    filesystem.remove_directory(tmp_dir)
    
if __name__ == "__main__":
  unit_test.main()
