#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
import os.path as path
from bes.common.variable import variable

class test_variable(unit_test):

  def test_find_variables(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just $foo') )
    self.assertEqual( [ 'foo' ], variable.find_variables('$foo') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is $foo and $bar') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('$foo$bar') )

  def test_find_variables_brackets(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just ${foo}') )
    self.assertEqual( [ 'foo' ], variable.find_variables('${foo}') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is ${foo} and ${bar}') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('${foo}${bar}') )

  def test_find_variables_mixed(self):
    self.assertEqual( [ 'bar', 'baz', 'foo', 'pip' ], variable.find_variables('This is $foo and ${bar} and ${baz} plus $pip') )

  def test_2find_variables(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just $foo') )
    self.assertEqual( [ 'foo' ], variable.find_variables('$foo') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is $foo and $bar') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('$foo$bar') )

  def test_2find_variables_parenthesis(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just $(foo)') )
    self.assertEqual( [ 'foo' ], variable.find_variables('$(foo)') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is $(foo) and $(bar)') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('$(foo)$(bar)') )

  def test_2find_variables_brackets(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just ${foo}') )
    self.assertEqual( [ 'foo' ], variable.find_variables('${foo}') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is ${foo} and ${bar}') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('${foo}${bar}') )

  def test_2find_variables_at_sign(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [], variable.find_variables('No vars @here neithers') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just @foo@') )
    self.assertEqual( [ 'foo' ], variable.find_variables('@foo@') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is @foo@ and @bar@') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('@foo@@bar@') )

  def test_2find_mixed(self):
    self.assertEqual( [ 'bar', 'baz', 'foo', 'pip' ], variable.find_variables('This is $foo and ${bar} and ${baz} plus @pip@') )

  def test_substitute_single_var_dollar_only(self):
    self.assertEqual( 'X', variable.substitute('$foo', { 'foo': 'X' }) )
    self.assertEqual( 'X', variable.substitute('$f', { 'f': 'X' }) )
    self.assertEqual( '$foo', variable.substitute('$foo', {}) )
    
  def test_substitute_single_var_bracket(self):
    self.assertEqual( 'X', variable.substitute('${foo}', { 'foo': 'X' }) )
    self.assertEqual( 'X', variable.substitute('${f}', { 'f': 'X' }) )
    self.assertEqual( '${foo}', variable.substitute('${foo}', {}) )
    
  def test_substitute_single_var_parentesis(self):
    self.assertEqual( 'X', variable.substitute('$(foo)', { 'foo': 'X' }) )
    self.assertEqual( 'X', variable.substitute('$(f)', { 'f': 'X' }) )
    self.assertEqual( '$(foo)', variable.substitute('$(foo)', {}) )
    
  def test_substitute_single_var_at_sign(self):
    self.assertEqual( 'X', variable.substitute('@foo@', { 'foo': 'X' }) )
    self.assertEqual( 'X', variable.substitute('@f@', { 'f': 'X' }) )
    self.assertEqual( '@foo@', variable.substitute('@foo@', {}) )
    
  def test_substitute_single_var_percent(self):
    self.assertEqual( 'X', variable.substitute('%foo%', { 'foo': 'X' }) )
    self.assertEqual( 'X', variable.substitute('%f%', { 'f': 'X' }) )
    self.assertEqual( '%foo%', variable.substitute('%foo%', {}) )
    
  def test_substitute(self):
    self.assertEqual( 'X and Y', variable.substitute('$foo and $bar', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'XY', variable.substitute('$foo$bar', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'X', variable.substitute('$foo', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'Y', variable.substitute('$bar', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '$not', variable.substitute('$not', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '', variable.substitute('$foo$bar$foo$bar', { 'foo': '', 'bar': '' }) )

  def test_ubstitute2(self):
    self.assertEqual( 'X and Y', variable.substitute('$foo and $bar', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'XY', variable.substitute('$foo$bar', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'X', variable.substitute('$foo', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'Y', variable.substitute('$bar', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '$not', variable.substitute('$not', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '', variable.substitute('$foo$bar$foo$bar', { 'foo': '', 'bar': '' }) )

  def test_substitute_brackets(self):
    self.assertEqual( 'X and Y', variable.substitute('${foo} and ${bar}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'XY', variable.substitute('${foo}${bar}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'X', variable.substitute('${foo}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'Y', variable.substitute('${bar}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '${not}', variable.substitute('${not}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '', variable.substitute('${foo}${bar}${foo}${bar}', { 'foo': '', 'bar': '' }) )

  def test_substitute_mixed(self):
    self.assertEqual( 'X and Y and Z and A', variable.substitute('$foo and ${bar} and ${baz} and $PIP',
                                                                  { 'foo': 'X', 'bar': 'Y', 'baz': 'Z', 'PIP': 'A' }) )

  def test_substitute_word_boundary(self):
    self.assertEqual( 'X and Y and Z', variable.substitute('${foo} and ${foo_bar} and ${foo_bar_baz}',
                                                           { 'foo': 'X', 'foo_bar': 'Y', 'foo_bar_baz': 'Z' }) )

  def test_substitute_word_boundary(self):
    self.assertEqual( 'X and Y and Z', variable.substitute('$foo and $foo_bar and $foo_bar_baz',
                                                           { 'foo': 'X', 'foo_bar': 'Y', 'foo_bar_baz': 'Z' }) )

  def test_has_rogue_dollar_signs(self):
    self.assertTrue( variable.has_rogue_dollar_signs('$foo') )
    self.assertFalse( variable.has_rogue_dollar_signs(r'\$foo') )

  def test_invalid_key(self):
    with self.assertRaises(TypeError) as context:
      variable.substitute('$foo and $bar', { 'foo': [ 'x' ], 'bar': 'Y' })

  def test_substitute_nested(self):
    self.assertEqual( 'X and ZY and Z', variable.substitute('${foo} and ${bar} and ${kiwi}', { 'foo': 'X', 'bar': '${kiwi}Y', 'kiwi': 'Z' }) )

  def test_substitute_escaped(self):
    self.assertEqual( r'X and c:\tmp\foo.txt', variable.substitute('${foo} and ${bar}', { 'foo': 'X', 'bar': r'c:\tmp\foo.txt' }) )

  def test_something(self):
    self.assertEqual( 'c_kiwi', variable.substitute('${v_something}', { 'v_something': 'c_kiwi' }) )

  def test_callable(self):
    self.assertEqual( '42', variable.substitute('${v_num}', { 'v_num': lambda: '42' }) )

  def test_is_single_variable(self):
    self.assertEqual( False, variable.is_single_variable('foo') )
    self.assertEqual( False, variable.is_single_variable('kiwi $foo') )
    self.assertEqual( True, variable.is_single_variable('${foo}') )
    self.assertEqual( True, variable.is_single_variable('$(foo)') )
    
if __name__ == '__main__':
  unit_test.main()
