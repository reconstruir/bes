#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.match import matcher_re

class Testmatcher_re(unittest.TestCase):

  def test_re_matcher_case(self):
    m = matcher_re('^.*something.*$', ignore_case = True)
    self.assertTrue( m.match('SOMETHING') )
    self.assertTrue( m.match('fooSOMETHING') )
    self.assertTrue( m.match('SOMETHINGbar') )
    self.assertFalse( m.match('SOMETHIN') )

  def test_re_matcher_case(self):
    m = matcher_re('^.*something.*$', ignore_case = True)
    self.assertTrue( m.match('SOMETHING') )
    self.assertTrue( m.match('fooSOMETHING') )
    self.assertTrue( m.match('SOMETHINGbar') )
    self.assertFalse( m.match('SOMETHIN') )


if __name__ == "__main__":
  unittest.main()
