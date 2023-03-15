#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bfile_match import bfile_match
from bes.files.match.bfile_matcher_options import bfile_matcher_options
from bes.files.bfile_entry import bfile_entry
from bes.files.bfile_entry_list import bfile_entry_list

from bes.testing.unit_test import unit_test

class test_bfile_match(unit_test):
                                     
  def test_match_fnmatch_one_matcher_any(self):
    m = bfile_match()
    m.add_matcher_fnmatch('*.py')
    self.assertEqual( True, m.match(bfile_entry('kiwi.py'), options = None, match_type = 'any') )
    self.assertEqual( False, m.match(bfile_entry('KIWI.PY'), options = None, match_type = 'any') )
    self.assertEqual( True, m.match(bfile_entry('/tmp/x/lemon.py'), options = None, match_type = 'any') )
    
  def test_match_fnmatch_one_matcher_any_with_ignore_case(self):
    m = bfile_match()
    m.add_matcher_fnmatch('*.py')
    options = bfile_matcher_options(ignore_case = True)
    self.assertEqual( True, m.match(bfile_entry('kiwi.py'), options = options) )
    self.assertEqual( True, m.match(bfile_entry('KIWI.PY'), options = options) )
    self.assertEqual( True, m.match(bfile_entry('/tmp/x/lemon.py'), options = options) )

  def test_match_fnmatch_one_matcher_any_with_path_type_basename(self):
    m = bfile_match()
    m.add_matcher_fnmatch('f*')
    options = bfile_matcher_options(path_type = 'basename')
    self.assertEqual( False, m.match(bfile_entry('fruit/kiwi.py'), options = options) )
    self.assertEqual( True, m.match(bfile_entry('fruit/fig.py'), options = options) )
    self.assertEqual( False, m.match(bfile_entry('FIG.PY'), options = options) )
    self.assertEqual( False, m.match(bfile_entry('/tmp/x/lemon.py'), options = options) )

  def test_match_fnmatch_one_matcher_any_with_ignore_case_and_path_type_basename(self):
    m = bfile_match()
    m.add_matcher_fnmatch('f*')
    options = bfile_matcher_options(ignore_case = True,
                                    path_type = 'basename')
    self.assertEqual( False, m.match(bfile_entry('fruit/kiwi.py'), options = options) )
    self.assertEqual( True, m.match(bfile_entry('fruit/fig.py'), options = options) )
    self.assertEqual( True, m.match(bfile_entry('FIG.PY'), options = options) )
    self.assertEqual( False, m.match(bfile_entry('/tmp/x/lemon.py'), options = options) )
    
  def test_match_fnmatch_two_matchers_all(self):
    m = bfile_match()
    m.add_matcher_fnmatch('*.py')
    m.add_matcher_fnmatch('k*')
    
    self.assertEqual( True, m.match(bfile_entry('kiwi.py'), match_type = 'all') )
    self.assertEqual( False, m.match(bfile_entry('lemon.py'), match_type = 'all') )
    self.assertEqual( False, m.match(bfile_entry('melon.txt'), match_type = 'all') )

  def test_match_fnmatch_two_matchers_any(self):
    m = bfile_match()
    m.add_matcher_fnmatch('*.py')
    m.add_matcher_fnmatch('k*')

    self.assertEqual( True, m.match(bfile_entry('kiwi.txt'), match_type = 'any') )
    self.assertEqual( True, m.match(bfile_entry('lemon.py'), match_type = 'any') )
    self.assertEqual( False, m.match(bfile_entry('melon.txt'), match_type = 'any') )

  def test_match_entries_fnmatch_one_matcher_any(self):
    patterns = [
      '*.txt',
      '*.pdf',
    ]
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    expected = [
      'notes.txt',
      'report.pdf',
      '/foo/bar/vaca.txt',
    ]
    m = bfile_match()
    m.add_matcher_fnmatch(patterns)
    self.assertEqual( bfile_entry_list(expected), m.match_entries(filenames) )
    
if __name__ == '__main__':
  unit_test.main()
