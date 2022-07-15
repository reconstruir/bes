#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.system._detail.ps_output_parser import ps_output_parser as P

class test_ps_output_parser(unit_test):

  def test_parse_ps_output_line(self):
    text = '''\
_hidd              151   1.7  0.0  6177388   9492   ??  Ss   31Dec69  46:20.56 /usr/libexec/hidd\
'''
    self.assertEqual( ( '_hidd', '151', '1.7', '0.0', '6177388', '9492', '??', 'Ss', '31Dec69', '46:20.56', '/usr/libexec/hidd' ),
                      P.parse_ps_output_line(text, 11) )

  def test_parse_ps_output_line(self):
    text = '''\
_hidd              151   1.7  0.0  6177388   9492   ??  Ss   31Dec69  46:20.56 /Applications/Foo Bar.app/Contents/MacOS/foobar -quick -slow\
'''
    self.assertEqual( ( '_hidd', '151', '1.7', '0.0', '6177388', '9492', '??', 'Ss', '31Dec69', '46:20.56', '/Applications/Foo Bar.app/Contents/MacOS/foobar -quick -slow' ),
                      P.parse_ps_output_line(text, 11) )
    
if __name__ == '__main__':
  unit_test.main()
