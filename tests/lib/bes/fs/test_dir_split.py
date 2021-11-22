#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.fs.dir_split import dir_split
from bes.fs.dir_split_options import dir_split_options
from bes.fs.testing.temp_content import temp_content

class dir_split_tester(object):

  _content = namedtuple('_content', 'name, num')
  @classmethod
  def make_content(clazz, content_desc, content_multiplier, extra_content_items = None):
    extra_content_items = extra_content_items or []
    content_desc = [ clazz._content(c.name, c.num * content_multiplier) for c in content_desc ]
    content_items = []
    for next_desc in content_desc:
      for i in range(1, next_desc.num + 1):
        filename = '{}{}.txt'.format(next_desc.name, i)
        text = 'this is {}'.format(filename)
        desc = 'file src/{} "{}" 644'.format(filename, text)
        content_items.append(desc)
    content_items.extend(extra_content_items)
    tmp_dir = temp_content.write_items_to_temp_dir(content_items)
    return tmp_dir

  _test_result = namedtuple('_test', 'tmp_dir, src_dir, dst_dir, src_files, dst_files, rv')
  
class test_dir_split(unit_test):

  def test_split_chunks_of_two(self):
    t = self._do_test([
      dir_split_tester._content('apple', 5),
      dir_split_tester._content('kiwi', 2),
      dir_split_tester._content('lemon', 3),
      dir_split_tester._content('blueberry', 1),
    ], 1, 2)
    expected = [
      'chunk-1/apple1.txt',
      'chunk-1/apple2.txt',
      'chunk-2/apple3.txt',
      'chunk-2/apple4.txt',
      'chunk-3/apple5.txt',
      'chunk-3/blueberry1.txt',
      'chunk-4/kiwi1.txt',
      'chunk-4/kiwi2.txt',
      'chunk-5/lemon1.txt',
      'chunk-5/lemon2.txt',
      'chunk-6/lemon3.txt',
    ]
    self.assertEqual( expected, t.dst_files )
    self.assertEqual( [], t.src_files )

  def test_split_chunks_of_one(self):
    t = self._do_test([
      dir_split_tester._content('apple', 5),
      dir_split_tester._content('kiwi', 2),
      dir_split_tester._content('lemon', 3),
      dir_split_tester._content('blueberry', 1),
    ], 1, 1)
    expected = [
      'chunk-01/apple1.txt',
      'chunk-02/apple2.txt',
      'chunk-03/apple3.txt',
      'chunk-04/apple4.txt',
      'chunk-05/apple5.txt',
      'chunk-06/blueberry1.txt',
      'chunk-07/kiwi1.txt',
      'chunk-08/kiwi2.txt',
      'chunk-09/lemon1.txt',
      'chunk-10/lemon2.txt',
      'chunk-11/lemon3.txt',
    ]
    self.assertEqual( expected, t.dst_files )
    self.assertEqual( [], t.src_files )

  def test_split_one_chunk(self):
    t = self._do_test([
      dir_split_tester._content('apple', 1),
      dir_split_tester._content('kiwi', 1),
    ], 1, 3)
    expected = [
      'chunk-1/apple1.txt',
      'chunk-1/kiwi1.txt',
    ]
    self.assertEqual( expected, t.dst_files )
    self.assertEqual( [], t.src_files )
    
  def test_split_larger_dir(self):
    t = self._do_test([
      dir_split_tester._content('apple', 5),
      dir_split_tester._content('kiwi', 2),
      dir_split_tester._content('lemon', 3),
      dir_split_tester._content('blueberry', 1),
    ], 3, 3)
    expected = [
      'chunk-01/apple1.txt',
      'chunk-01/apple10.txt',
      'chunk-01/apple11.txt',
      'chunk-02/apple12.txt',
      'chunk-02/apple13.txt',
      'chunk-02/apple14.txt',
      'chunk-03/apple15.txt',
      'chunk-03/apple2.txt',
      'chunk-03/apple3.txt',
      'chunk-04/apple4.txt',
      'chunk-04/apple5.txt',
      'chunk-04/apple6.txt',
      'chunk-05/apple7.txt',
      'chunk-05/apple8.txt',
      'chunk-05/apple9.txt',
      'chunk-06/blueberry1.txt',
      'chunk-06/blueberry2.txt',
      'chunk-06/blueberry3.txt',
      'chunk-07/kiwi1.txt',
      'chunk-07/kiwi2.txt',
      'chunk-07/kiwi3.txt',
      'chunk-08/kiwi4.txt',
      'chunk-08/kiwi5.txt',
      'chunk-08/kiwi6.txt',
      'chunk-09/lemon1.txt',
      'chunk-09/lemon2.txt',
      'chunk-09/lemon3.txt',
      'chunk-10/lemon4.txt',
      'chunk-10/lemon5.txt',
      'chunk-10/lemon6.txt',
      'chunk-11/lemon7.txt',
      'chunk-11/lemon8.txt',
      'chunk-11/lemon9.txt',
    ]
    self.assertEqual( expected, t.dst_files )
    self.assertEqual( [], t.src_files )

  def _do_test(self, content_desc, content_multiplier, chunk_size, extra_content_items = None):
    options = dir_split_options(chunk_size = chunk_size,
                                prefix = 'chunk-')
    tmp_dir = dir_split_tester.make_content(content_desc,
                                            content_multiplier,
                                            extra_content_items = extra_content_items)
    src_dir = path.join(tmp_dir, 'src')
    dst_dir = path.join(tmp_dir, 'dst')
    dir_split.split(src_dir, dst_dir, options)
    src_files = file_find.find(src_dir, relative = True)
    dst_files = file_find.find(dst_dir, relative = True)
    return dir_split_tester._test_result(tmp_dir, src_dir, dst_dir, src_files, dst_files, None)
    
if __name__ == '__main__':
  unit_test.main()
