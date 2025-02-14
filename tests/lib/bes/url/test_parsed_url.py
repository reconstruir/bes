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
    self.assertEqual( 'something', _t('http://something.example/foo.cgi') )
    self.assertEqual( 'kiwi', _t('http://kiwi.io') )
    self.assertEqual( 'kiwi', _t('http://kiwi.notathing') )
    
  def test_remove_query(self):
    def _t(s):
      return parsed_url.parse(s).remove_query()
    self.assertEqual( 'http://www.example.com/foo.cgi', _t('http://www.example.com/foo.cgi?a=6&b=7&foo=666') )
    self.assertEqual( 'http://www.example.com/foo.cgi', _t('http://www.example.com/foo.cgi') )

  def test_remove_query_fields(self):
    def _t(s, c):
      return parsed_url.parse(s).remove_query_fields(c)
    self.assertEqual( 'http://www.example.com/foo.cgi?a=6&b=7',
                      _t('http://www.example.com/foo.cgi?a=6&b=7&foo=666', lambda kv: kv.key == 'foo') )
#    self.assertEqual( 'http://www.example.com/foo.cgi', _t('http://www.example.com/foo.cgi') )
    
  def test_normalized(self):
    def _t(s):
      return parsed_url.parse(s).normalized()
    self.assertEqual( 'http://www.example.com/', _t('http://www.example.com/') )
    self.assertEqual( 'http://www.example.com/', _t('http://www.example.com') )
    self.assertEqual( 'http://www.example.com/foo.cgi', _t('http://www.example.com/foo.cgi') )

  def test_without_address(self):
    def _t(s):
      return parsed_url.parse(s).without_address
    self.assertEqual( '', _t('http://www.example.com/') )
    self.assertEqual( '', _t('http://www.example.com') )
    self.assertEqual( 'foo.cgi', _t('http://www.example.com/foo.cgi') )
    self.assertEqual( 'foo.cgi?x=42', _t('http://www.example.com/foo.cgi?x=42') )
    self.assertEqual( 'foo.cgi?x=42&y=666', _t('http://www.example.com/foo.cgi?x=42&y=666') )
    self.assertEqual( 'foo.cgi?x=42&y=666', _t('foo.cgi?x=42&y=666') )

  def test_query_dict(self):
    def _t(s):
      return parsed_url.parse(s).query_dict
    self.assertEqual( { 'a': [ '6' ], 'b': [ '7' ], 'foo': [ '666' ] }, _t('http://www.example.com/foo.cgi?a=6&b=7&foo=666') )

  def test_query_key_values(self):
    def _t(s):
      return parsed_url.parse(s).query_key_values
    self.assertEqual( [ ( 'a', '6' ), ( 'b', '7' ), ( 'foo', '666' ) ], _t('http://www.example.com/foo.cgi?a=6&b=7&foo=666') )

  def test_replace_path(self):
    def _t(url, new_path):
      return str(parsed_url.parse(url).replace_path(new_path))
    self.assertEqual( 'http://www.example.com/coconut/', _t('http://www.example.com/kiwi/lemon/apple/', 'coconut') )
    self.assertEqual( 'http://www.example.com/coconut/', _t('http://www.example.com/kiwi/lemon/apple/', 'coconut/') )
    self.assertEqual( 'http://www.example.com/coconut', _t('http://www.example.com/kiwi/lemon/apple', 'coconut') )
    self.assertEqual( 'http://www.example.com/coconut', _t('http://www.example.com/kiwi/lemon/apple', 'coconut/') )
    
if __name__ == '__main__':
  unit_test.main()
