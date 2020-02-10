#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import math, string, random

from bes.testing.unit_test import unit_test

from bes.archive.temp_archive import temp_archive
from bes.archive.archiver import archiver
from bes.fs.file_util import file_util
from bes.fs.file_split import file_split

class test_file_split(unit_test):

  def test_split_basic(self):
    NUM_ITEMS = 10
    CONTENT_SIZE = 1024 * 100
    items = []
    for i in range(0, NUM_ITEMS):
      arcname = 'item{}.txt'.format(i)
      item = temp_archive.item(arcname, content = self._make_content(CONTENT_SIZE))
      items.append(item)
    tmp_archive = temp_archive.make_temp_archive(items, 'zip')

    files = file_split.split(tmp_archive, int(math.floor(file_util.size(tmp_archive) / 1)))
    unsplit_tmp_archive = self.make_temp_file()
    file_split.unsplit(unsplit_tmp_archive, files)
    self.assertEqual( file_util.checksum('sha256', tmp_archive), file_util.checksum('sha256', unsplit_tmp_archive) )

    files = file_split.split(tmp_archive, int(math.floor(file_util.size(tmp_archive) / 2)))
    unsplit_tmp_archive = self.make_temp_file()
    file_split.unsplit(unsplit_tmp_archive, files)
    self.assertEqual( file_util.checksum('sha256', tmp_archive), file_util.checksum('sha256', unsplit_tmp_archive) )

    files = file_split.split(tmp_archive, int(math.floor(file_util.size(tmp_archive) / 3)))
    unsplit_tmp_archive = self.make_temp_file()
    file_split.unsplit(unsplit_tmp_archive, files)
    self.assertEqual( file_util.checksum('sha256', tmp_archive), file_util.checksum('sha256', unsplit_tmp_archive) )
    
    files = file_split.split(tmp_archive, int(math.floor(file_util.size(tmp_archive) / 4)))
    unsplit_tmp_archive = self.make_temp_file()
    file_split.unsplit(unsplit_tmp_archive, files)
    self.assertEqual( file_util.checksum('sha256', tmp_archive), file_util.checksum('sha256', unsplit_tmp_archive) )
    
    files = file_split.split(tmp_archive, int(math.floor(file_util.size(tmp_archive) / 5)))
    unsplit_tmp_archive = self.make_temp_file()
    file_split.unsplit(unsplit_tmp_archive, files)
    self.assertEqual( file_util.checksum('sha256', tmp_archive), file_util.checksum('sha256', unsplit_tmp_archive) )
    
  @classmethod
  def _make_content(clazz, size):
    chars = [ c for c in string.ascii_letters ]
    v = []
    for i in range(0, size):
      i = random.randint(0, (len(chars) - 1))
      v.append(chars[i])
    return ''.join(v)
  
if __name__ == '__main__':
  unit_test.main()
