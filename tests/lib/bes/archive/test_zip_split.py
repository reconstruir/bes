#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string, random

from bes.testing.unit_test import unit_test

from bes.archive.temp_archive import temp_archive
from bes.archive.zip_split import zip_split
from bes.archive.archiver import archiver
from bes.fs.file_util import file_util

class test_zip_split(unit_test):

  def test_split_basic(self):
    NUM_ITEMS = 10
    CONTENT_SIZE = 1024 * 100
    items = []
    for i in range(0, NUM_ITEMS):
      arcname = 'item{}.txt'.format(i)
      item = temp_archive.item(arcname, content = self._make_content(CONTENT_SIZE))
      items.append(item)
    tmp_archive = temp_archive.make_temp_archive(items, 'zip')
    self.assertEqual( [
      'item0.txt',
      'item1.txt',
      'item2.txt',
      'item3.txt',
      'item4.txt',
      'item5.txt',
      'item6.txt',
      'item7.txt',
      'item8.txt',
      'item9.txt',
    ], archiver.members(tmp_archive) )

    MAX_SIZE = file_util.size(tmp_archive) / 4

    files = zip_split.split(tmp_archive, MAX_SIZE)
    self.assertEqual( 4, len(files) )

    self.assertEqual( [
      'item0.txt',
      'item1.txt',
    ], archiver.members(files[0]) )
    self.assertEqual( [
      'item2.txt',
      'item3.txt',
      'item4.txt',
    ], archiver.members(files[1]) )
    self.assertEqual( [
      'item5.txt',
      'item6.txt',
      'item7.txt',
    ], archiver.members(files[2]) )
    self.assertEqual( [
      'item8.txt',
      'item9.txt',
    ], archiver.members(files[3]) )
    
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
