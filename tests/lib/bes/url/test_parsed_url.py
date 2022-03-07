#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.url.parsed_url import parsed_url

class test_parsed_url(unit_test):

  def test_parse(self):
    f = parsed_url.parse
    self.assertEqual( ( 'http', 'www.example.com', '/foo.cgi', '', '', '' ), f('http://www.example.com/foo.cgi') )

  def test_netloc(self):
    def _t(s):
      return parsed_url.parse(s).netloc
    self.assertEqual( 'www.example.com', _t('http://www.example.com/foo.cgi') )
    
  def test_netloc_name(self):
    def _t(s):
      return parsed_url.parse(s).netloc_name
    self.assertEqual( 'example', _t('http://www.example.com/foo.cgi') )
    self.assertEqual( 'example', _t('http://example.com/foo.cgi') )
    self.assertEqual( 'example', _t('http://example.edu/foo.cgi') )
    self.assertEqual( 'example', _t('http://something.example/foo.cgi') )
    
  def test_remove_query(self):
    def _t(s):
      return parsed_url.parse(s).remove_query()
    self.assertEqual( 'http://www.example.com/foo.cgi', _t('http://www.example.com/foo.cgi?a=6&b=7&foo=666') )
    self.assertEqual( 'http://www.example.com/foo.cgi', _t('http://www.example.com/foo.cgi') )

  def test_normalized(self):
    def _t(s):
      return parsed_url.parse(s).normalized()
    self.assertEqual( 'http://www.example.com/', _t('http://www.example.com/') )
    self.assertEqual( 'http://www.example.com/', _t('http://www.example.com') )
    self.assertEqual( 'http://www.example.com/foo.cgi', _t('http://www.example.com/foo.cgi') )


if __name__ == '__main__':
  unit_test.main()
