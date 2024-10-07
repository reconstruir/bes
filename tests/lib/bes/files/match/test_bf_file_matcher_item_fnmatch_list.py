#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_file_matcher_item_fnmatch_list import bf_file_matcher_item_fnmatch_list
from bes.files.match.bf_file_matcher_options import bf_file_matcher_options
from bes.files.bf_entry import bf_entry

from bes.testing.unit_test import unit_test

class test_bf_file_matcher_item_fnmatch_list(unit_test):
  
  def test_match_no_options_all(self):
    self.assertEqual( True, self._match([ '*.py' ], 'ALL', 'kiwi.py', None) )
    self.assertEqual( False, self._match([ '*.py', 'something*' ], 'ALL', 'something.pdf', None) )
    self.assertEqual( False, self._match([ '*.py' ], 'ALL', 'KIWI.PY', None) )
    self.assertEqual( True, self._match([ '*.py' ], 'ALL', '/tmp/x/lemon.py', None) )

  def test_match_no_options_any(self):
    self.assertEqual( True, self._match([ '*.py' ], 'ANY', 'kiwi.py', None) )
    self.assertEqual( True, self._match([ '*.py', 'something*' ], 'ANY', 'something.pdf', None) )
    self.assertEqual( False, self._match([ '*.py' ], 'ANY', 'KIWI.PY', None) )
    self.assertEqual( True, self._match([ '*.py' ], 'ANY', '/tmp/x/lemon.py', None) )

  def test_match_no_options_none(self):
    self.assertEqual( False, self._match([ '*.py' ], 'NONE', 'kiwi.py', None) )
    self.assertEqual( False, self._match([ '*.py', 'something*' ], 'NONE', 'something.pdf', None) )
    self.assertEqual( True, self._match([ '*.py' ], 'NONE', 'KIWI.PY', None) )
    self.assertEqual( False, self._match([ '*.py' ], 'NONE', '/tmp/x/lemon.py', None) )

  def test_match_with_both_included_and_excluded_patterns(self):
    self.assertEqual( True, self._match_ie([ '*.py' ], [ '.*git*' ], 'src/kiwi.py', '/proj') )
    self.assertEqual( False, self._match_ie([ '*.py' ], [ '.*git*' ], '.git/cache', '/proj') )
    self.assertEqual( True, self._match_ie([ '*.py' ], [ '.*git*' ], 'src/kiwi/.git/foo', '/proj') )
    
  def _match(self, patterns, match_type, filename, root_dir, **options):
    entry = bf_entry(filename, root_dir = root_dir)
    matcher = bf_file_matcher_item_fnmatch_list(patterns, match_type)
    return matcher.match(entry, bf_file_matcher_options(**options))

  def _match_ie(self, include_patterns, exclude_patterns, filename, root_dir, **options):
    entry = bf_entry(filename, root_dir = root_dir)
    matcher = bf_file_matcher_item_fnmatch_list(include_patterns, 'ALL')
    matcher = bf_file_matcher_item_fnmatch_list(exclude_patterns, 'NONE')
    return matcher.match(entry, bf_file_matcher_options(**options))
  
if __name__ == '__main__':
  unit_test.main()
