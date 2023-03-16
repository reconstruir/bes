#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bfile_matcher_re import bfile_matcher_re
from bes.files.match.bfile_matcher_options import bfile_matcher_options
from bes.files.bfile_entry import bfile_entry

from bes.testing.unit_test import unit_test

class test_bfile_matcher_re(unit_test):
  
  def test_match_no_options(self):
    self.assertEqual( True, self._match('.*\.py', 'kiwi.py') )
    self.assertEqual( False, self._match('.*\.py', 'KIWI.PY') )
    self.assertEqual( True, self._match('.*\.py', '/tmp/x/lemon.py') )

  def test_match_ignore_case(self):
    self.assertEqual( True, self._match('.*\.py', 'kiwi.py', ignore_case = True) )
    self.assertEqual( True, self._match('.*\.py', 'KIWI.PY', ignore_case = True) )
    self.assertEqual( True, self._match('.*\.py', '/tmp/x/lemon.py', ignore_case = True) )

  def test_match_path_type_basename(self):
    self.assertEqual( True, self._match('k.*\.py', '/foo/bar/kiwi.py', path_type = 'basename') )
    self.assertEqual( False, self._match('k.*\.py', 'koo/bar/melon.py', path_type = 'basename') )

  def _match(self, pattern, filename, **options):
    entry = bfile_entry(filename)
    matcher = bfile_matcher_re(pattern)
    return matcher.match(entry, bfile_matcher_options(**options))
  
if __name__ == '__main__':
  unit_test.main()
