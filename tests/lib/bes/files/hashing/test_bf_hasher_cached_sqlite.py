#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from datetime import timedelta

from bes.testing.unit_test import unit_test

from bes.files.hashing.bf_hasher_cached_sqlite import bf_hasher_cached_sqlite
from bes.files.bf_date import bf_date

class test_bf_hasher_cached_sqlite(unit_test):

  def _make_tmp_db(self):
    tmp_db_filename = path.join(self.make_temp_dir(), 'test.db')
    return bf_hasher_cached_sqlite(tmp_db_filename)

  def test_get_checksum(self):
    db = self._make_tmp_db()
    tmp = self.make_temp_file(content = 'kiwi')
    self.assertEqual( 0, db.num_computations )
    self.assertEqual( '1a5afeda973d776e31d1d7266f184468f84d99bed311d88d3dcb67015934f9f9', db.get_checksum(tmp) )
    self.assertEqual( 1, db.num_computations )
    self.assertEqual( '1a5afeda973d776e31d1d7266f184468f84d99bed311d88d3dcb67015934f9f9', db.get_checksum(tmp) )
    self.assertEqual( 1, db.num_computations )

  def test_get_checksum_with_collision(self):
    db = self._make_tmp_db()
    tmp1 = self.make_temp_file(content = 'kiwi')
    tmp2 = self.make_temp_file(content = 'kiwx')
    bf_date.set_modification_date(tmp2, bf_date.get_modification_date(tmp1))
    self.assertEqual( 0, db.num_computations )
    self.assertEqual( '1a5afeda973d776e31d1d7266f184468f84d99bed311d88d3dcb67015934f9f9', db.get_checksum(tmp1) )
    self.assertEqual( 1, db.num_computations )
    self.assertEqual( '65ffbe9c3eb9f18542a813d11e4be9cee0799bff47a29082c12ebc31c5e4eb08', db.get_checksum(tmp2) )
    self.assertEqual( 2, db.num_computations )

  def test_get_checksum_with_mtime_changed(self):
    db = self._make_tmp_db()
    tmp = self.make_temp_file(content = 'kiwx')
    self.assertEqual( 0, db.num_computations )
    self.assertEqual( '65ffbe9c3eb9f18542a813d11e4be9cee0799bff47a29082c12ebc31c5e4eb08', db.get_checksum(tmp) )
    self.assertEqual( 1, db.num_computations )
    mtime = bf_date.get_modification_date(tmp)
    delta = timedelta(days = -666)
    bf_date.set_modification_date(tmp, mtime + delta)
    self.assertEqual( '65ffbe9c3eb9f18542a813d11e4be9cee0799bff47a29082c12ebc31c5e4eb08', db.get_checksum(tmp) )
    self.assertEqual( 2, db.num_computations )
    
if __name__ == '__main__':
  unit_test.main()
