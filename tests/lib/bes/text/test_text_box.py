#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat.StringIO import StringIO

from bes.testing.unit_test import unit_test
from bes.text.text_box import text_box_ascii
from bes.text.text_box import text_box_unicode

class test_text_box_writer(unit_test):

  def test_ascii(self):
    t = text_box_ascii()
    buf = StringIO()
    t.write_h_bar(buf)
    t.write_v_bar(buf)
    t.write_tl_corner(buf)
    t.write_tr_corner(buf)
    self.assertEqual( '-|++', buf.getvalue() )
    
  def test_unicode(self):
    t = text_box_unicode()
    buf = StringIO()
    t.write_h_bar(buf)
    t.write_v_bar(buf)
    t.write_tl_corner(buf)
    t.write_tr_corner(buf)
    self.assertEqual( '\xe2\x94\x80\xe2\x94\x82\xe2\x94\x8c\xe2\x94\x90', buf.getvalue() )
    
if __name__ == '__main__':
  unit_test.main()
