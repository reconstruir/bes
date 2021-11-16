#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.fs.dir_split import dir_split
from bes.fs.testing.temp_content import temp_content

class test_dir_split(unit_test):

  _content = namedtuple('_content', 'name, num')
 
  def test_split(self):
    t = self._do_test([
      self._content('apple', 5),
      self._content('kiwi', 2),
      self._content('lemon', 3),
      self._content('blueberry', 1),
    ], 3, 3)
    expected = [
      'split-01/apple1.txt',
      'split-01/apple10.txt',
      'split-01/apple11.txt',
      'split-02/apple12.txt',
      'split-02/apple13.txt',
      'split-02/apple14.txt',
      'split-03/apple15.txt',
      'split-03/apple2.txt',
      'split-03/apple3.txt',
      'split-04/apple4.txt',
      'split-04/apple5.txt',
      'split-04/apple6.txt',
      'split-05/apple7.txt',
      'split-05/apple8.txt',
      'split-05/apple9.txt',
      'split-06/blueberry1.txt',
      'split-06/blueberry2.txt',
      'split-06/blueberry3.txt',
      'split-07/kiwi1.txt',
      'split-07/kiwi2.txt',
      'split-07/kiwi3.txt',
      'split-08/kiwi4.txt',
      'split-08/kiwi5.txt',
      'split-08/kiwi6.txt',
      'split-09/lemon1.txt',
      'split-09/lemon2.txt',
      'split-09/lemon3.txt',
      'split-10/lemon4.txt',
      'split-10/lemon5.txt',
      'split-10/lemon6.txt',
      'split-11/lemon7.txt',
      'split-11/lemon8.txt',
      'split-11/lemon9.txt',
    ]
    self.assertEqual( expected, t.dst_files )

  _test = namedtuple('_test', 'tmp_dir, src_dir, dst_dir, src_files, dst_files')
  def _do_test(self, content_desc, content_multiplier, num_chunks):
    content_desc = [ self._content(c.name, c.num * content_multiplier) for c in content_desc ]
    content_items = []
    for next_desc in content_desc:
      for i in range(1, next_desc.num + 1):
        filename = '{}{}.txt'.format(next_desc.name, i)
        text = 'this is {}'.format(filename)
        desc = 'file src/{} "{}" 644'.format(filename, text)
        content_items.append(desc)
    tmp_dir = temp_content.write_items_to_temp_dir(content_items)
    src_dir = path.join(tmp_dir, 'src')
    dst_dir = path.join(tmp_dir, 'dst')
    dir_split.split(src_dir, dst_dir, 'split-', num_chunks)
    src_files = file_find.find(src_dir, relative = True)
    dst_files = file_find.find(dst_dir, relative = True)
    return self._test(tmp_dir, src_dir, dst_dir, src_files, dst_files)
    
if __name__ == '__main__':
  unit_test.main()
