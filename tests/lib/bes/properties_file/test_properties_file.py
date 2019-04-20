#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from os import path
from bes.fs import temp_file

from bes.testing.unit_test import unit_test
from bes.properties_file.properties_file import properties_file as PF

class test_properties_file(unit_test):

  def test_read(self):
    text = """\
fruit: 'kiwi'
status: 'doomed'
version: '1.2.3'
"""
    tmp = temp_file.make_temp_file(content = text)
    self.assertEqual( {
      'fruit': 'kiwi',
      'status': 'doomed',
      'version': '1.2.3',
    }, PF.read(tmp) )
    
  def test_read_to_tuple(self):
    text = """\
fruit: 'kiwi'
status: 'doomed'
version: '1.2.3'
"""
    tmp = temp_file.make_temp_file(content = text)

    TC = namedtuple('TC', 'fruit, status, version')
    self.assertEqual( ( 'kiwi', 'doomed', '1.2.3' ), PF.read_to_tuple(tmp, TC) )
    
  def test_read_to_tuple_missing_fields(self):
    text = """\
fruit: 'kiwi'
version: '1.2.3'
"""
    tmp = temp_file.make_temp_file(content = text)

    TC = namedtuple('TC', 'fruit, status, version')
    self.assertEqual( ( 'kiwi', None, '1.2.3' ), PF.read_to_tuple(tmp, TC) )
    
  def test_read_to_tuple_empty(self):
    tmp = temp_file.make_temp_file()
    TC = namedtuple('TC', 'fruit, status, version')
    self.assertEqual( ( None, None, None ), PF.read_to_tuple(tmp, TC) )

  def test_read_indent(self):
    text = """\
  fruit: 'kiwi'
 status: 'doomed'
version: '1.2.3'
"""
    tmp = temp_file.make_temp_file(content = text)
    self.assertEqual( {
      'fruit': 'kiwi',
      'status': 'doomed',
      'version': '1.2.3',
    }, PF.read(tmp) )
    
  def test_read_to_tuple_layered(self):
    text1 = """\
fruit: 'kiwi'
status: 'doomed'
version: '1.2.3'
"""
    text2 = """\
fruit: 'orange'
status: 'doomed'
version: '1.2.4'
"""
    tmp1 = temp_file.make_temp_file(content = text1)
    tmp2 = temp_file.make_temp_file(content = text2)

    TC = namedtuple('TC', 'fruit, status, version')
    self.assertEqual( ( 'orange', 'doomed', '1.2.4' ), PF.read_to_tuple_layered([ tmp1, tmp2 ], TC) )
    
    
if __name__ == '__main__':
  unit_test.main()
