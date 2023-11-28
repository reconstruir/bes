#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.text.bindent import bindent

class test_bindent(unit_test):

  def test_indent_two(self):
    text = '''\
kiwi
orange
melon
'''

    expected = '''\
  kiwi
  orange
  melon
'''
    self.assertEqual( expected, bindent.indent(text, 2) )

  def test_indent_four(self):
    text = '''\
kiwi
orange
melon
'''

    expected = '''\
    kiwi
    orange
    melon
'''
    self.assertEqual( expected, bindent.indent(text, 4) )
    
if __name__ == '__main__':
  unit_test.main()
