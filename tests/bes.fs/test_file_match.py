#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.fs import file_match

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
      '.*\.txt$',
      '.*\.pdf$',
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
      '.*\.txt$',
      '.*\.pdf$',
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
      '.*\.txt$',
      '.*\.pdf$',
    ]
    expected = [
    ]
    self.assertEqual( sorted(expected), file_match.match_re(filenames, expressions, file_match.ALL) )

    expressions = [
      '.*\.txt$',
      'n.*$',
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
    expected = [
      'vaca.png',
    ]
    def _func(filename): return filename.endswith('.png')
    self.assertEqual( sorted(expected), file_match.match_function(filenames, _func) )
    
if __name__ == "__main__":
  unittest.main()
