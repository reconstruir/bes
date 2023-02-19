#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from datetime import datetime
from datetime import timedelta
import os.path as path

from bes.files.bfile_date import bfile_date
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media

from bes.testing.unit_test import unit_test
from bes.files.attr.bfile_attr_mtime_cached import bfile_attr_mtime_cached
from bes.docker.docker import docker

class test_bfile_attr_mtime_cached(unit_test):
  
  @classmethod
  def setUpClass(clazz):
    docker.raise_skip_if_running_under_docker()

  def test_get_cached_bytes(self):
    tmp = self.make_temp_file(dir = __file__, content = 'foo')
    value = '666'.encode('utf-8')
    def _value_maker(f):
      return value
    self.assertEqual( value, bfile_attr_mtime_cached.get_cached_bytes(tmp, 'foo', _value_maker) )
    self.assertEqual( [ '__bes_mtime_foo__', 'foo' ], bfile_attr_mtime_cached.keys(tmp) )
    self.assertEqual( '666', bfile_attr_mtime_cached.get_string(tmp, 'foo') )

  def test_get_cached_bytes_with_change(self):
    tmp = self.make_temp_file(dir = __file__, content = 'this is foo', suffix = '.txt')
    yesterday = datetime.now() - timedelta(days = 1)
    bfile_date.set_modification_date(tmp, yesterday)

    counter = 0
    def _value_maker1(f):
      nonlocal counter
      counter += 1
      return b'666'

    def _value_maker2(f):
      nonlocal counter
      counter += 1
      return b'667'
    
    self.assertEqual( 0, counter )
    self.assertEqual( b'666', bfile_attr_mtime_cached.get_cached_bytes(tmp, 'foo', _value_maker1) )
    self.assertEqual( 1, counter )
    self.assertEqual( b'666', bfile_attr_mtime_cached.get_cached_bytes(tmp, 'foo', _value_maker1) )
    self.assertEqual( 1, counter )
    mtime = bfile_date.get_modification_date(tmp)
    self.assertEqual( {
      '__bes_mtime_foo__': str(mtime.timestamp()).encode('utf-8'),
      'foo': b'666',
    }, bfile_attr_mtime_cached.get_all(tmp) )

    with open(tmp, 'a') as f:
      f.write(' more text')
      f.flush()

    with open(tmp, 'r') as f:
      tmp_content = f.read()
      self.assertEqual( 'this is foo more text', tmp_content )

    self.assertEqual( b'667', bfile_attr_mtime_cached.get_cached_bytes(tmp, 'foo', _value_maker2) )
    self.assertEqual( 2, counter )
    self.assertEqual( b'667', bfile_attr_mtime_cached.get_cached_bytes(tmp, 'foo', _value_maker2) )
    self.assertEqual( 2, counter )
  
    new_mtime = bfile_date.get_modification_date(tmp)
    
    self.assertEqual( {
      '__bes_mtime_foo__': str(new_mtime.timestamp()).encode('utf-8'),
      'foo': b'667',
    }, bfile_attr_mtime_cached. get_all(tmp) )
    
if __name__ == '__main__':
  unit_test.main()
