#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.url.url_util import url_util

class test_url_util(unit_test):

  def test_remove_query(self):
    f = url_util.remove_query
    self.assertEqual( 'http://www.example.com/foo.cgi', f('http://www.example.com/foo.cgi?a=6&b=7&foo=666') )

  def test_normalize(self):
    f = url_util.normalize
    self.assertEqual( 'http://www.example.com/foo.cgi', f('http://www.example.com/foo.cgi') )
    self.assertEqual( 'http://www.example.com/', f('http://www.example.com') )
    self.assertEqual( 'http://www.example.com/', f('http://www.example.com/') )

  def test_make_file_url(self):
    f = url_util.make_file_url
#    self.assertEqual( 'file:///foo/bar/kiwi.txt', f(self.xp_filename(self.make_abspath('/foo/bar/kiwi.txt'))) )
    self.assertEqual( 'file:///foo/bar/kiwi.txt', f('/foo/bar/kiwi.txt') )
    
if __name__ == '__main__':
  unit_test.main()
