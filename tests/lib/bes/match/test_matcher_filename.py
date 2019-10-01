#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.match.matcher_filename import matcher_filename
from bes.match.matcher_filename import matcher_multiple_filename

class test_matcher_filename(unittest.TestCase):

  def test_filename_matcher(self):
    m = matcher_filename('*.jpg')

    self.assertTrue( m.match('caca.jpg') )
    self.assertFalse( m.match('caca.JPG') )
    self.assertFalse( m.match('caca.png') )

  def test_filename_matcher_case(self):
    m = matcher_filename('*.jpg', ignore_case = True)

    self.assertTrue( m.match('CACA.JPG') )
    self.assertTrue( m.match('CACA.jpg') )
    self.assertFalse( m.match('caca.png') )
    self.assertFalse( m.match('CACA.PNG') )

  def test_filename_multi_matcher(self):
    m = matcher_multiple_filename([ '*.jpg', '*.png' ])

    self.assertTrue( m.match('caca.jpg') )
    self.assertTrue( m.match('caca.png') )
    self.assertFalse( m.match('caca.pdf') )
    self.assertFalse( m.match('caca.tif') )

  def test_filter(self):
    stuff = [
      'foo.txt',
      'foo.txt~',
      '.#foo.txt',
      'foo.txt.backup',
      'FOO.TXT',
      'bar.txt',
      'bar.png',
    ]      

    self.assertEqual( [ 'foo.txt', '.#foo.txt', 'bar.txt' ], matcher_filename('*.txt').filter(stuff) )
    self.assertEqual( [ 'bar.png' ], matcher_filename('*.png').filter(stuff) )

  def test_custom_filter(self):

    class Backupfile_matcher(matcher_multiple_filename):

      PATTERNS = [
        '.#*',
        '*~',
        '*.backup',
      ]

      def __init__(self):
        super(Backupfile_matcher, self).__init__(self.PATTERNS, ignore_case = True)

    stuff = [
      'foo.txt',
      'foo.txt~',
      '.#foo.txt',
      'foo.txt.backup',
      'FOO.TXT',
      'bar.txt',
      'bar.png',
    ]      

    self.assertEqual( [ 'foo.txt~', '.#foo.txt', 'foo.txt.backup' ], Backupfile_matcher().filter(stuff) )
    self.assertEqual( [ 'foo.txt', 'FOO.TXT', 'bar.txt', 'bar.png' ], Backupfile_matcher().filter(stuff, negate = True) )

if __name__ == "__main__":
  unittest.main()
