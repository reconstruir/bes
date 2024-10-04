#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.files.find.bf_walk import bf_walk
from bes.fs.testing.temp_content import temp_content
from bes.system.log import logger

from bes.testing.unit_test import unit_test

class test_bf_walk(unit_test):

  _log = logger('bf_walk')
  
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  _walk_result = namedtuple('_walk_result', 'tmp_dir, result')
  def _walk(self, items, **kwargs):
    tmp_dir = self._make_temp_content(items)
    result = [ x for x in bf_walk.walk(tmp_dir, **kwargs) ]
    hacked_result = []
    for item in result:
      hacked_item = (
        item[0].replace(tmp_dir, '${tmp_dir}'),
        item[1],
        item[2],
        item[3],
      )
      hacked_result.append(hacked_item)
    return self._walk_result(tmp_dir, hacked_result)

  def test_walk_basic(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    self.assertEqual( [
      ( '${tmp_dir}', ['emptydir', 'subdir'], ['emptyfile.txt', 'foo.txt'], 0 ),
      ( '${tmp_dir}/emptydir', [], [], 1 ),
      ( '${tmp_dir}/subdir', ['subberdir'], ['bar.txt'], 1 ),
      ( '${tmp_dir}/subdir/subberdir', [], ['baz.txt'], 2 ),
    ], self._walk(content).result )
if __name__ == '__main__':
  unit_test.main()
