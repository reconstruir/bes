#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.url.parsed_url import parsed_url

class test_parsed_url(unit_test):

  def test_parse(self):
    f = parsed_url.parse
    self.assertEqual( ( 'http', 'www.example.com', '/foo.cgi', '', '', '' ), f('http://www.example.com/foo.cgi') )

  def xtest_remove_query(self):
    f = url_util.remove_query
    self.assertEqual( 'http://www.example.com/foo.cgi', f('http://www.example.com/foo.cgi?a=6&b=7&foo=666') )

  def xtest_normalize(self):
    f = url_util.normalize
    self.assertEqual( 'http://www.example.com/foo.cgi', f('http://www.example.com/foo.cgi') )
    self.assertEqual( 'http://www.example.com/', f('http://www.example.com') )
    self.assertEqual( 'http://www.example.com/', f('http://www.example.com/') )
    
if __name__ == '__main__':
  unit_test.main()
