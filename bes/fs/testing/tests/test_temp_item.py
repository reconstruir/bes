#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.testing import temp_item as I

class test_temp_item(unit_test):

  def test_parse_string(self):
    self.assertEqual( I( I.FILE, 'foo.txt', 'this is foo\nhaha', None ), I.parse('file foo.txt "this is foo\nhaha"') )
    self.assertEqual( ( I.FILE, 'foo.txt', None, None ), I.parse('file foo.txt') )
    self.assertEqual( ( I.DIR, 'foo', None, None ), I.parse('dir foo') )
    self.assertEqual( ( I.FILE, 'foo.txt', None, 0755 ), I.parse('file foo.txt "" 755') )

  def test_parse_tuple(self):
    self.assertEqual( ( I.FILE, 'foo.txt', 'this is foo\nhaha' ), I.parse( ('file', 'foo.txt', 'this is foo\nhaha') ) )

if __name__ == "__main__":
  unit_test.main()
