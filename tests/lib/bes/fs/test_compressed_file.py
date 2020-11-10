#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.compressed_file import compressed_file
from bes.fs.file_util import file_util

class test_compressed_file(unit_test):

  def test_basic(self):

    content = '''\
This is my nice file.
'''

    tmp_file = self.make_temp_file(content = content)
    tmp_compressed_file = self.make_temp_file()
    compressed_file.compress(tmp_file, tmp_compressed_file)

    tmp_uncompressed_file = self.make_temp_file()
    compressed_file.uncompress(tmp_compressed_file, tmp_uncompressed_file)

    self.assertMultiLineEqual( file_util.read(tmp_file, codec = 'utf-8'), file_util.read(tmp_uncompressed_file, codec = 'utf-8') )
    
if __name__ == '__main__':
  unit_test.main()
