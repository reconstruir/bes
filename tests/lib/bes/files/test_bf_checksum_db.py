#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test

from bes.files.bf_checksum_db import bf_checksum_db

class test_bf_checksum_db(unit_test):

  def _make_tmp_db(self):
    tmp_db_filename = path.join(self.make_temp_dir(), 'test.db')
    return bf_checksum_db(tmp_db_filename)

  def test_get_checksum(self):
    db = self._make_tmp_db()
    tmp1 = self.make_temp_file(content = 'kiwi')
    tmp2 = self.make_temp_file(content = 'orange')
    self.assertEqual( '1a5afeda973d776e31d1d7266f184468f84d99bed311d88d3dcb67015934f9f9', db.get_checksum(tmp1) )
    self.assertEqual( '1a5afeda973d776e31d1d7266f184468f84d99bed311d88d3dcb67015934f9f9', db.get_checksum(tmp1) )

if __name__ == '__main__':
  unit_test.main()
