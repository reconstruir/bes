#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.match.bf_match import bf_match
from bes.files.match.bf_match_options import bf_match_options
from bes.files.bfile_entry import bfile_entry
from bes.files.bfile_entry_list import bfile_entry_list

from bes.testing.unit_test import unit_test

class test_bf_match(unit_test):

  def _match(self, setup, filename, root_dir, **options_kargs):
    matcher = bf_match()
    setup(matcher)
    entry = bfile_entry(filename, root_dir = root_dir)
    options = bf_match_options(**options_kargs)
    return matcher.match(entry, options = options)

  def test_match_fnmatch_one_matcher_any(self):
    def setup(m):
      m.add_matcher_fnmatch('*.py')
      
    self.assertEqual( True, self._match(setup, 'kiwi.py', None) )
    self.assertEqual( False, self._match(setup, 'KIWI.PY', None) )
    self.assertEqual( True, self._match(setup, '/tmp/x/lemon.py', None) )
    
  def test_match_fnmatch_one_matcher_any_with_ignore_case(self):
    def setup(m):
      m.add_matcher_fnmatch('*.py')
      
    self.assertEqual( True, self._match(setup, 'kiwi.py', None, ignore_case = True) )
    self.assertEqual( True, self._match(setup, 'KIWI.PY', None, ignore_case = True) )
    self.assertEqual( True, self._match(setup, '/tmp/x/lemon.py', None, ignore_case = True) )

  def test_match_fnmatch_one_matcher_any_with_path_type_basename(self):
    def setup(m):
      m.add_matcher_fnmatch('f*')
      
    options = bf_match_options(path_type = 'basename')
    #self.assertEqual( False, self._match(setup, 'fruit/kiwi.py', None, path_type = 'basename') )
    #self.assertEqual( True, self._match(setup, 'fruit/fig.py', None, path_type = 'basename') )
    self.assertEqual( False, self._match(setup, 'FIG.PY', None, path_type = 'basename') )
    #self.assertEqual( False, self._match(setup, '/tmp/x/lemon.py', None, path_type = 'basename') )

  def test_match_fnmatch_one_matcher_any_with_ignore_case_and_path_type_basename(self):
    def setup(m):
      m.add_matcher_fnmatch('f*')
      
    options = { 'ignore_case': True, 'path_type': 'basename' }
    self.assertEqual( False, self._match(setup, 'fruit/kiwi.py', None, **options) )
    self.assertEqual( True, self._match(setup, 'fruit/fig.py', None, **options) )
    self.assertEqual( True, self._match(setup, 'FIG.PY', None, **options) )
    self.assertEqual( False, self._match(setup, '/tmp/x/lemon.py', None, **options) )
    
  def test_match_fnmatch_two_matchers_all(self):
    def setup(m):
      m.add_matcher_fnmatch('*.py')
      m.add_matcher_fnmatch('k*')
    
    self.assertEqual( True, self._match(setup, 'kiwi.py', None, match_type = 'all') )
    self.assertEqual( False, self._match(setup, 'lemon.py', None, match_type = 'all') )
    self.assertEqual( False, self._match(setup, 'melon.txt', None, match_type = 'all') )

    
  def test_match_fnmatch_two_matchers_none(self):
    def setup(m):
      m.add_matcher_fnmatch('*.py')
      m.add_matcher_fnmatch('k*')
    
    self.assertEqual( False, self._match(setup, 'kiwi.py', None, match_type = 'none') )
    self.assertEqual( False, self._match(setup, 'lemon.py', None, match_type = 'none') )
    self.assertEqual( True, self._match(setup, 'melon.txt', None, match_type = 'none') )
    
  def test_match_fnmatch_two_matchers_any(self):
    def setup(m):
      m.add_matcher_fnmatch('*.py')
      m.add_matcher_fnmatch('k*')

    self.assertEqual( True, self._match(setup, 'kiwi.txt', None, match_type = 'any') )
    self.assertEqual( True, self._match(setup, 'lemon.py', None, match_type = 'any') )
    self.assertEqual( False, self._match(setup, 'melon.txt', None, match_type = 'any') )

  def test_match_entries_fnmatch_two_matchers_any(self):
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
    m = bf_match()
    m.add_matcher_fnmatch('*.txt')
    m.add_matcher_fnmatch('*.pdf')
    self.assertEqual( bfile_entry_list(expected), m.match_entries(filenames) )
    
if __name__ == '__main__':
  unit_test.main()
