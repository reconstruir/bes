#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.find.bfile_filename_matcher_fnmatch import bfile_filename_matcher_fnmatch
from bes.files.find.bfile_filename_matcher_options import bfile_filename_matcher_options

from bes.testing.unit_test import unit_test

class test_bfile_filename_matcher_fnmatch(unit_test):
  
  def test_match_one_pattern_all(self):
    self.assertEquals( True, self._match(bfile_filename_matcher_fnmatch('*.py', 'ALL'),
                                         'foo.py') )

  def _match(self, matcher, filename, **options):
    opts = bfile_filename_matcher_options(**options)
    return matcher.match(filename, opts)
                                     
if __name__ == '__main__':
  unit_test.main()
