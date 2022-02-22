#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.dir_operation_item import dir_operation_item
from bes.fs.dir_operation_item_list import dir_operation_item_list
from bes.testing.unit_test import unit_test

class test_dir_operation_item_list(unit_test):

  def test__make_resolved_filename(self):
    f = dir_operation_item_list._make_resolved_filename
    self.assertEqual( '/a/b/12345-666-foo.txt', f('/a/b/foo.txt', '12345', 666) )
    
if __name__ == '__main__':
  unit_test.main()
