#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.fs.file_match import file_match

class test_file_match(unittest.TestCase):

  def test_match_fnmatch_any(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    patterns = [
      '*.txt',
      '*.pdf',
    ]
    expected = [
      'notes.txt',
      'report.pdf',
      '/foo/bar/vaca.txt',
    ]
    self.assertEqual( sorted(expected), file_match.match_fnmatch(filenames, patterns, file_match.ANY) )
 
  def test_match_fnmatch_none(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    patterns = [
      '*.txt',
      '*.pdf',
    ]
    expected = [
      'caca.jpg',
      'vaca.png',
    ]
    self.assertEqual( sorted(expected), file_match.match_fnmatch(filenames, patterns, file_match.NONE) )

  def test_match_fnmatch_all(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    patterns = [
      '*.txt',
      '*.pdf',
    ]
    expected = [
    ]
    self.assertEqual( sorted(expected), file_match.match_fnmatch(filenames, patterns, file_match.ALL) )

    patterns = [
      '*.txt',
      'n*',
    ]
    expected = [
      'notes.txt',
    ]
    self.assertEqual( sorted(expected), file_match.match_fnmatch(filenames, patterns, file_match.ALL) )

  def test_match_re_any(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    expressions = [
      r'.*\.txt$',
      r'.*\.pdf$',
    ]
    expected = [
      'notes.txt',
      'report.pdf',
      '/foo/bar/vaca.txt',
    ]
    self.assertEqual( sorted(expected), file_match.match_re(filenames, expressions, file_match.ANY) )
 
  def test_match_re_none(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    expressions = [
      r'.*\.txt$',
      r'.*\.pdf$',
    ]
    expected = [
      'caca.jpg',
      'vaca.png',
    ]
    self.assertEqual( sorted(expected), file_match.match_re(filenames, expressions, file_match.NONE) )

  def test_match_re_all(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    expressions = [
      r'.*\.txt$',
      r'.*\.pdf$',
    ]
    expected = [
    ]
    self.assertEqual( sorted(expected), file_match.match_re(filenames, expressions, file_match.ALL) )

    expressions = [
      r'.*\.txt$',
      r'n.*$',
    ]
    expected = [
      'notes.txt',
    ]
    self.assertEqual( sorted(expected), file_match.match_re(filenames, expressions, file_match.ALL) )

  def test_match_function(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    self.assertEqual( [
      'vaca.png',
    ], file_match.match_function(filenames, lambda f: f.endswith('.png')) )
    
  def test_match_function_with_match_type(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    self.assertEqual( [
      'vaca.png',
    ], file_match.match_function(filenames, lambda f: f.endswith('.png'), match_type = 'ANY') )
    self.assertEqual( [
      'vaca.png',
    ], file_match.match_function(filenames, lambda f: f.endswith('.png'), match_type = 'ALL') )
    self.assertEqual( [
      '/foo/bar/vaca.txt',
      'caca.jpg',
      'notes.txt',
      'report.pdf',
    ], file_match.match_function(filenames, lambda f: f.endswith('.png'), match_type = 'NONE') )
    
  def test_match_function_with_basename(self):
    filenames = [
      'notes.txt',
      'report.pdf',
      'caca.jpg',
      'vaca.png',
      '/foo/bar/vaca.txt',
    ]
    self.assertEqual( [
    ], file_match.match_function(filenames, lambda f: f.startswith('/'), basename = True) )
    self.assertEqual( [
      '/foo/bar/vaca.txt',
    ], file_match.match_function(filenames, lambda f: f.startswith('/'), basename = False) )
    
if __name__ == '__main__':
  unittest.main()
