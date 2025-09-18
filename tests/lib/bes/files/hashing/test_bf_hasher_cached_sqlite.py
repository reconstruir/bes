#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from datetime import timedelta

from bes.testing.unit_test import unit_test

from bes.files.hashing.bf_hasher_cached_sqlite import bf_hasher_cached_sqlite
from bes.files.bf_date import bf_date
from bes.files.bf_entry import bf_entry

class test_bf_hasher_cached_sqlite(unit_test):

  def _make_tmp_db(self):
    tmp_db_filename = path.join(self.make_temp_dir(), 'test.db')
    return bf_hasher_cached_sqlite(tmp_db_filename)

  def _make_temp_entry(self, content = None):
    tmp = self.make_temp_file(content = content)
    return bf_entry(tmp)
  
  def test_checksum_sha256(self):
    db = self._make_tmp_db()
    content = 'this is kiwi'
    tmp = self._make_temp_entry(content = content)
    self.assertEqual( 0, db.num_computations )
    self.assertEqual( 'b215a9c68299bf9f1ab7d430e965ae40bf3920841d6555e31534c70938617d6f', db.checksum_sha256(tmp) )
    self.assertEqual( 1, db.num_computations )
    self.assertEqual( 'b215a9c68299bf9f1ab7d430e965ae40bf3920841d6555e31534c70938617d6f', db.checksum_sha256(tmp) )
    self.assertEqual( 1, db.num_computations )
  
  def test_checksum_sha256_with_collision(self):
    db = self._make_tmp_db()
    tmp1 = self._make_temp_entry(content = 'kiwi')
    tmp2 = self._make_temp_entry(content = 'kiwx')
    bf_date.set_modification_date(tmp2.filename, bf_date.get_modification_date(tmp1.filename))
    self.assertEqual( 0, db.num_computations )
    self.assertEqual( '1a5afeda973d776e31d1d7266f184468f84d99bed311d88d3dcb67015934f9f9', db.checksum_sha256(tmp1) )
    self.assertEqual( 1, db.num_computations )
    self.assertEqual( '65ffbe9c3eb9f18542a813d11e4be9cee0799bff47a29082c12ebc31c5e4eb08', db.checksum_sha256(tmp2) )
    self.assertEqual( 2, db.num_computations )

  def test_checksum_sha256_with_mtime_changed(self):
    db = self._make_tmp_db()
    tmp = self._make_temp_entry(content = 'kiwx')
    self.assertEqual( 0, db.num_computations )
    self.assertEqual( '65ffbe9c3eb9f18542a813d11e4be9cee0799bff47a29082c12ebc31c5e4eb08', db.checksum_sha256(tmp) )
    self.assertEqual( 1, db.num_computations )
    mtime = bf_date.get_modification_date(tmp.filename)
    delta = timedelta(days = -666)
    bf_date.set_modification_date(tmp.filename, mtime + delta)
    self.assertEqual( '65ffbe9c3eb9f18542a813d11e4be9cee0799bff47a29082c12ebc31c5e4eb08', db.checksum_sha256(tmp) )
    self.assertEqual( 2, db.num_computations )

  def test_short_checksum_sha256(self):
    db = self._make_tmp_db()
    content = 'this is kiwi'
    tmp = self._make_temp_entry(content = content)
    self.assertEqual( 0, db.num_computations )
    self.assertEqual( 'b215a9c68299bf9f1ab7d430e965ae40bf3920841d6555e31534c70938617d6f', db.short_checksum_sha256(tmp) )
    self.assertEqual( 1, db.num_computations )
    self.assertEqual( 'b215a9c68299bf9f1ab7d430e965ae40bf3920841d6555e31534c70938617d6f', db.short_checksum_sha256(tmp) )
    self.assertEqual( 1, db.num_computations )
  
  def test_short_checksum_sha256_with_collision(self):
    db = self._make_tmp_db()
    tmp1 = self._make_temp_entry(content = 'kiwi')
    tmp2 = self._make_temp_entry(content = 'kiwx')
    bf_date.set_modification_date(tmp2.filename, bf_date.get_modification_date(tmp1.filename))
    self.assertEqual( 0, db.num_computations )
    self.assertEqual( '1a5afeda973d776e31d1d7266f184468f84d99bed311d88d3dcb67015934f9f9', db.short_checksum_sha256(tmp1) )
    self.assertEqual( 1, db.num_computations )
    self.assertEqual( '65ffbe9c3eb9f18542a813d11e4be9cee0799bff47a29082c12ebc31c5e4eb08', db.short_checksum_sha256(tmp2) )
    self.assertEqual( 2, db.num_computations )
    
if __name__ == '__main__':
  unit_test.main()
