#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common.variable_manager import variable_manager
from bes.key_value.key_value_list import key_value_list

class test_variable_manager(unit_test):

  def test_substitute(self):
    v = variable_manager()
    v.add_variables(key_value_list.parse('FOO=1.2.3 BAR=abcdefg'))
    self.assertEqual( 'FOO is 1.2.3; BAR is abcdefg', v.substitute('FOO is ${FOO}; BAR is ${BAR}') )
    
  def test_substitute_dict(self):
    v = variable_manager()
    v.add_variables({ 'FOO': '1.2.3', 'BAR': 'abcdefg' })
    self.assertEqual( 'FOO is 1.2.3; BAR is abcdefg', v.substitute('FOO is ${FOO}; BAR is ${BAR}') )

  def test___init__(self):
    vl = {'v_comment_begin': ';', 'v_key_value_delimiter': '='}
    vm = variable_manager(variables = {'v_comment_begin': ';', 'v_key_value_delimiter': '='},
                          add_system_variables = False)
    self.assertEqual( ';', vm.substitute('${v_comment_begin}') )
    
if __name__ == '__main__':
  unit_test.main()
