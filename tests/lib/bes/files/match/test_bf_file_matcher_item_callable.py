#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_file_matcher_item_callable import bf_file_matcher_item_callable
from bes.files.match.bf_file_matcher_options import bf_file_matcher_options
from bes.files.bf_entry import bf_entry

from bes.testing.unit_test import unit_test

class test_bf_file_matcher_item_callable(unit_test):
  
  def test_match_one_func_all(self):
    f = lambda entry, filename: filename.endswith('.py')
    self.assertEqual( True, self._match(f, 'kiwi.py') )
    self.assertEqual( False, self._match(f, 'KIWI.PY') )
    self.assertEqual( True, self._match(f, '/tmp/x/lemon.py') )

  def xtest_match_two_funcs_all(self):
    self.assertEqual( True, self._match( ( lambda f: f.startswith('k'), f ), 'kiwi.py', match_type = 'ALL') )
    self.assertEqual( False, self._match( ( lambda f: f.startswith('k'), f ), 'lemon.py', match_type = 'ALL') )

  def xtest_match_two_funcs_any(self):
    self.assertEqual( True, self._match( ( lambda f: f.startswith('k'), f ), 'kiwi.py', match_type = 'ANY') )
    self.assertEqual( True, self._match( ( lambda f: f.startswith('k'), f ), 'lemon.py', match_type = 'ANY') )

  def _match(self, patterns, filename, **options):
    entry = bf_entry(filename)
    matcher = bf_file_matcher_item_callable(patterns)
    return matcher.match(entry, bf_file_matcher_options(**options))
  
if __name__ == '__main__':
  unit_test.main()
