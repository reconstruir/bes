#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_mime import file_mime
from bes.fs.file_util import file_util
from bes.fs.file_attributes_metadata import file_attributes_metadata
from bes.fs.file_attributes import file_attributes

class test_file_attributes_metadata(unit_test):

  def test_get_bytes(self):
    tmp = self.make_temp_file(content = 'this is foo', suffix = '.txt')
    yesterday = datetime.now() - timedelta(days = 1)
    file_util.set_modification_date(tmp, yesterday)

    counter = 0
    def _value_maker1():
      nonlocal counter
      counter += 1
      return b'666'

    def _value_maker2():
      nonlocal counter
      counter += 1
      return b'667'
    
    self.assertEqual( 0, counter )
    self.assertEqual( b'666', file_attributes_metadata.get_bytes(tmp, 'foo', _value_maker1) )
    self.assertEqual( 1, counter )
    self.assertEqual( b'666', file_attributes_metadata.get_bytes(tmp, 'foo', _value_maker1) )
    self.assertEqual( 1, counter )
    self.assertEqual( {
      '__bes_mtime_foo__': str(yesterday.timestamp()).encode('utf-8'),
      'foo': b'666',
    }, file_attributes.get_all(tmp) )

    with open(tmp, 'a') as f:
      f.write(' more text')
      f.flush()

    self.assertEqual( 'this is foo more text', file_util.read(tmp, codec = 'utf-8') )

    new_mtime = file_util.get_modification_date(tmp)

    self.assertEqual( b'667', file_attributes_metadata.get_bytes(tmp, 'foo', _value_maker2) )
    self.assertEqual( 2, counter )
    self.assertEqual( b'667', file_attributes_metadata.get_bytes(tmp, 'foo', _value_maker2) )
    self.assertEqual( 2, counter )

    self.assertEqual( {
      '__bes_mtime_foo__': str(new_mtime.timestamp()).encode('utf-8'),
      'foo': b'667',
    }, file_attributes.get_all(tmp) )
    
#  def test_modification_date(self):
#    yesterday = datetime.now() - timedelta(days = 1)
#    tmp = self.make_temp_file()
#    m1 = file_util.get_modification_date(tmp)
#    file_util.set_modification_date(tmp, yesterday)
#    self.assertEqual( yesterday, file_util.get_modification_date(tmp) )
#    self.assertNotEqual( m1, file_util.get_modification_date(tmp) )
    
if __name__ == '__main__':
  unit_test.main()
