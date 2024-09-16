#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_file_matcher_item_fnmatch_list import bf_file_matcher_item_fnmatch_list
from bes.files.match.bf_file_matcher_options import bf_file_matcher_options
from bes.files.bf_entry import bf_entry

from bes.testing.unit_test import unit_test

class test_bf_file_matcher_item_fnmatch_list(unit_test):
  
  def test_match_no_options_all(self):
    self.assertEqual( True, self._match([ '*.py' ], 'ALL', 'kiwi.py') )
    self.assertEqual( False, self._match([ '*.py', 'something*' ], 'ALL', 'something.pdf') )
    self.assertEqual( False, self._match([ '*.py' ], 'ALL', 'KIWI.PY') )
    self.assertEqual( True, self._match([ '*.py' ], 'ALL', '/tmp/x/lemon.py') )

  def test_match_no_options_any(self):
    self.assertEqual( True, self._match([ '*.py' ], 'ANY', 'kiwi.py') )
    self.assertEqual( True, self._match([ '*.py', 'something*' ], 'ANY', 'something.pdf') )
    self.assertEqual( False, self._match([ '*.py' ], 'ANY', 'KIWI.PY') )
    self.assertEqual( True, self._match([ '*.py' ], 'ANY', '/tmp/x/lemon.py') )

  def test_match_no_options_none(self):
    self.assertEqual( False, self._match([ '*.py' ], 'NONE', 'kiwi.py') )
    self.assertEqual( False, self._match([ '*.py', 'something*' ], 'NONE', 'something.pdf') )
    self.assertEqual( True, self._match([ '*.py' ], 'NONE', 'KIWI.PY') )
    self.assertEqual( False, self._match([ '*.py' ], 'NONE', '/tmp/x/lemon.py') )
    
  def _match(self, patterns, match_type, filename, **options):
    entry = bf_entry(filename)
    matcher = bf_file_matcher_item_fnmatch_list(patterns, match_type)
    return matcher.match(entry, bf_file_matcher_options(**options))
                                     
if __name__ == '__main__':
  unit_test.main()
