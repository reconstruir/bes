#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_resolver_item import file_resolver_item
from bes.fs.file_resolver_item_list import file_resolver_item_list
from bes.testing.unit_test import unit_test

class test_file_resolver_item_list(unit_test):

  def test_basename_map(self):
    l = file_resolver_item_list()
    apple = file_resolver_item('/foo', 'a/apple.txt', 0, 0)
    kiwi = file_resolver_item('/foo', 'b/kiwi.txt', 1, 1)
    l.append(apple)
    l.append(kiwi)
    self.assertEqual( {
      'apple.txt': [ apple ], 
      'kiwi.txt': [ kiwi ], 
    }, l.basename_map() )

  def test_duplicate_basename_map(self):
    l = file_resolver_item_list()
    apple = file_resolver_item('/foo', 'a/apple.txt', 0, 0)
    kiwi = file_resolver_item('/foo', 'b/kiwi.txt', 1, 1)
    l.append(apple)
    l.append(kiwi)
    self.assertEqual( {}, l.duplicate_basename_map() )
    kiwi2 = file_resolver_item('/foo', 'c/kiwi.txt', 2, 2)
    l.append(kiwi2)
    self.assertEqual( {
      'kiwi.txt': [ '/foo/b/kiwi.txt', '/foo/c/kiwi.txt' ],
    }, l.duplicate_basename_map() )
    
if __name__ == "__main__":
  unit_test.main()
