#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from bes.text import section_parser as P

class test_entry_parser(unit_test):

  def test_empty(self):
    self.assertEqual( [], self._parse('') )
    
  def xtest_parse_simple(self):
    self.assertEqual( [], self._parse('foo="BAR BAZ"') )

  def xtest_parse_single_quoted(self):
    self.assertEqual( [ 'f o o', 'b a r' ], self._parse('"f o o" "b a r"') )
    self.assertEqual( [ 'f o o', 'b a r' ], self._parse('f\ o\ o b\ a\ r') )

  def xtest_parse_quote_values(self):
    self.assertEqual( [ '-DNAME="f o o"', '"b a r"' ], self._parse('-DNAME="f o o" "b a r"', keep_quotes = True) )
    self.assertEqual( [ '-DNAME=f o o', 'b a r' ], self._parse('-DNAME=f\ o\ o b\ a\ r', keep_quotes = True) )
    self.assertEqual( [ '-DNAME="foo bar"' ], self._parse('-DNAME="foo bar"', keep_quotes = True) )
    self.assertEqual( [ '-DNAME=\\"foo bar\\"' ], self._parse('-DNAME="foo bar"', keep_quotes = True, escape_quotes = True) )

  @classmethod
  def _parse(self, text):
    return P.parse_to_list(text)

if __name__ == '__main__':
  unit_test.main()
