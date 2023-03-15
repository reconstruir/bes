#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bfile_matcher_fnmatch import bfile_matcher_fnmatch
from bes.files.match.bfile_matcher_options import bfile_matcher_options
from bes.files.bfile_entry import bfile_entry

from bes.testing.unit_test import unit_test

class test_bfile_matcher_fnmatch(unit_test):
  
  def test_match_one_pattern_all(self):
    self.assertEqual( True, self._match('*.py', 'kiwi.py', match_type = 'ALL') )
    self.assertEqual( False, self._match('*.py', 'KIWI.PY', match_type = 'ALL') )
    self.assertEqual( True, self._match('*.py', '/tmp/x/lemon.py', match_type = 'ALL') )

  def test_match_two_patterns_all(self):
    self.assertEqual( True, self._match( ( 'k*', '*.py' ), 'kiwi.py', match_type = 'ALL') )
    self.assertEqual( False, self._match( ('k*', '*.py' ), 'lemon.py', match_type = 'ALL') )

  def test_match_two_patterns_any(self):
    self.assertEqual( True, self._match( ( 'k*', '*.py' ), 'kiwi.py', match_type = 'ANY') )
    self.assertEqual( True, self._match( ( 'k*', '*.py' ), 'lemon.py', match_type = 'ANY') )
    
  def _match(self, patterns, filename, **options):
    entry = bfile_entry(filename)
    matcher = bfile_matcher_fnmatch(patterns)
    return matcher.match(entry, bfile_matcher_options(**options))
                                     
if __name__ == '__main__':
  unit_test.main()
