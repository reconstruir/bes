#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, unittest
from bes.fs.dir_util import dir_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content

class test_dir_util(unittest.TestCase):

  def __make_tmp_files(self):
    tmp_dir = temp_file.make_temp_dir()
    file_util.save(path.join(tmp_dir, 'foo.txt'), content = 'foo.txt\n')
    file_util.save(path.join(tmp_dir, 'bar.txt'), content = 'bar.txt\n')
    file_util.save(path.join(tmp_dir, 'kiwi.jpg'), content = 'kiwi.jpg\n')
    file_util.save(path.join(tmp_dir, 'kiwi.png'), content = 'kiwi.png\n')
    file_util.save(path.join(tmp_dir, 'orange.png'), content = 'orange.png\n')
    return tmp_dir

  def test(self):
    tmp_dir = self.__make_tmp_files()
    expected_files = [
      'foo.txt',
      'bar.txt',
      'kiwi.jpg',
      'kiwi.png',
      'orange.png',
    ]
    expected_files = [ path.join(tmp_dir, f) for f in expected_files ]
    self.assertEqual( sorted(expected_files), dir_util.list(tmp_dir) )

  def test_list_relative(self):
    tmp_dir = self.__make_tmp_files()
    expected_files = [
      'foo.txt',
      'bar.txt',
      'kiwi.jpg',
      'kiwi.png',
      'orange.png',
    ]
    self.assertEqual( sorted(expected_files), dir_util.list(tmp_dir, relative = True) )

  def test_list_pattern(self):
    tmp_dir = self.__make_tmp_files()
    self.assertEqual( [ 'kiwi.jpg' ], dir_util.list(tmp_dir, relative = True, patterns = '*.jpg') )
    self.assertEqual( [ 'kiwi.jpg', 'kiwi.png' ], dir_util.list(tmp_dir, relative = True, patterns = 'kiwi*') )

  def test_all_parents(self):
    self.assertEqual( [ '/', '/usr', '/usr/lib' ], dir_util.all_parents('/usr/lib/foo' ) )

  def test_move_files(self):
    tmp_dir = temp_file.make_temp_dir()
    src_dir = path.join(tmp_dir, 'src')
    dst_dir = path.join(tmp_dir, 'dst')
    file_util.mkdir(dst_dir)
    temp_content.write_items([
      'file foo.txt "This is foo.txt\n" 644',
      'file bar.txt "This is bar.txt\n" 644',
      'file sub1/sub2/baz.txt "This is baz.txt\n" 644',
      'file yyy/zzz/vvv.txt "This is vvv.txt\n" 644',
      'file .hidden "this is .hidden\n" 644',
      'file script.sh "#!/bin/bash\necho script.sh\nexit 0\n" 755',
      'file .hushlogin "" 644',
    ], src_dir)
    expected = [
      '.hidden',
      '.hushlogin',
      'bar.txt',
      'foo.txt',
      'script.sh',
      'sub1/sub2/baz.txt',
      'yyy/zzz/vvv.txt',
    ]
    self.assertEqual( expected, file_find.find(src_dir, relative = True))
    dir_util.move_files(src_dir, dst_dir)
    self.assertEqual( expected, file_find.find(dst_dir, relative = True))
    self.assertEqual( [], file_find.find(src_dir, relative = True))
    
if __name__ == "__main__":
  unittest.main()
