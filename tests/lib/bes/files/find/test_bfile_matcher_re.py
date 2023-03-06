#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.find.bfile_matcher_re import bfile_matcher_re
from bes.files.find.bfile_filename_matcher_options import bfile_filename_matcher_options
from bes.files.bfile_entry import bfile_entry

from bes.testing.unit_test import unit_test

class test_bfile_matcher_re(unit_test):
  
  def test_match_one_pattern_all(self):
    self.assertEquals( True, self._match(r'.*\.py', 'kiwi.py', match_type = 'ALL') )
    self.assertEquals( False, self._match('.*\.py', 'KIWI.PY', match_type = 'ALL') )
    self.assertEquals( True, self._match('.*\.py', '/tmp/x/lemon.py', match_type = 'ALL') )

  def test_match_two_patterns_all(self):
    self.assertEquals( True, self._match( ( 'k.*', '.*\.py' ), 'kiwi.py', match_type = 'ALL') )
    self.assertEquals( False, self._match( ( 'k.*', '.*\.py' ), 'lemon.py', match_type = 'ALL') )

  def test_match_two_patterns_any(self):
    self.assertEquals( True, self._match( ( 'k.*', '.*\.py' ), 'kiwi.py', match_type = 'ANY') )
    self.assertEquals( True, self._match( ( 'k.*', '.*\.py' ), 'lemon.py', match_type = 'ANY') )
    
  def _match(self, patterns, filename, **options_args):
    entry = bfile_entry(filename)
    options = bfile_filename_matcher_options(**options_args)
    matcher = bfile_matcher_re(patterns, options)
    return matcher.match(entry)
                                     
if __name__ == '__main__':
  unit_test.main()
