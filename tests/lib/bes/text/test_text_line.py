#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.text import text_line as TL

class test_text_line(unit_test):

  def test_text_no_comments(self):
    self.assertEqual( 'foo', TL(1, 'foo#comment').text_no_comments )
    
if __name__ == '__main__':
  unit_test.main()
