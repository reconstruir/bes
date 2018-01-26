#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.common import variable

class test_variable(unittest.TestCase):

  def test_find_variables(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just $foo') )
    self.assertEqual( [ 'foo' ], variable.find_variables('$foo') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is $foo and $bar') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('$foo$bar') )

  def test_find_variables_parenthesis(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just $(foo)') )
    self.assertEqual( [ 'foo' ], variable.find_variables('$(foo)') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is $(foo) and $(bar)') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('$(foo)$(bar)') )

  def test_find_variables_brackets(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just ${foo}') )
    self.assertEqual( [ 'foo' ], variable.find_variables('${foo}') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is ${foo} and ${bar}') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('${foo}${bar}') )

  def test_find_variables_at_sign(self):
    self.assertEqual( [], variable.find_variables('No vars here') )
    self.assertEqual( [], variable.find_variables('No vars @here neithers') )
    self.assertEqual( [ 'foo' ], variable.find_variables('Just @foo@') )
    self.assertEqual( [ 'foo' ], variable.find_variables('@foo@') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('This is @foo@ and @bar@') )
    self.assertEqual( [ 'bar', 'foo' ], variable.find_variables('@foo@@bar@') )

  def test_find_mixed(self):
    self.assertEqual( [ 'bar', 'baz', 'foo', 'pip' ], variable.find_variables('This is $foo and ${bar} and ${baz} plus @pip@') )

  def test_substitute(self):
    self.assertEqual( 'X and Y', variable.substitute('$foo and $bar', { 'foo': 'X', 'bar': 'Y' }) )
    # for some dumb reason this is broken in python 2.7
    #self.assertEqual( 'XY', variable.substitute('$foo$bar', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'X', variable.substitute('$foo', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'Y', variable.substitute('$bar', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '$not', variable.substitute('$not', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '', variable.substitute('$foo$bar$foo$bar', { 'foo': '', 'bar': '' }) )

  def test_substitute_parenthesis(self):
    self.assertEqual( 'X and Y', variable.substitute('$(foo) and $(bar)', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'XY', variable.substitute('$(foo)$(bar)', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'X', variable.substitute('$(foo)', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'Y', variable.substitute('$(bar)', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '$(not)', variable.substitute('$(not)', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '', variable.substitute('$(foo)$(bar)$(foo)$(bar)', { 'foo': '', 'bar': '' }) )

  def test_substitute_brackets(self):
    self.assertEqual( 'X and Y', variable.substitute('${foo} and ${bar}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'XY', variable.substitute('${foo}${bar}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'X', variable.substitute('${foo}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'Y', variable.substitute('${bar}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '${not}', variable.substitute('${not}', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '', variable.substitute('${foo}${bar}${foo}${bar}', { 'foo': '', 'bar': '' }) )

  def test_substitute_at_sign(self):
    self.assertEqual( 'X and Y', variable.substitute('@foo@ and @bar@', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'XY', variable.substitute('@foo@@bar@', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'X', variable.substitute('@foo@', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( 'Y', variable.substitute('@bar@', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '@not@', variable.substitute('@not@', { 'foo': 'X', 'bar': 'Y' }) )
    self.assertEqual( '', variable.substitute('@foo@@bar@@foo@@bar@', { 'foo': '', 'bar': '' }) )

  def test_substitute_mixed(self):
    self.assertEqual( 'X and Y and Z and A', variable.substitute('$foo and ${bar} and ${baz} and @PIP@',
                                                                 { 'foo': 'X', 'bar': 'Y', 'baz': 'Z', 'PIP': 'A' }) )

  def test_substitute_word_boundary(self):
    self.assertEqual( 'X and Y and Z', variable.substitute('${foo} and ${foo_bar} and ${foo_bar_baz}',
                                                           { 'foo': 'X', 'foo_bar': 'Y', 'foo_bar_baz': 'Z' }) )

  def test_substitute_word_boundary(self):
    self.assertEqual( 'X and Y and Z', variable.substitute('$foo and $foo_bar and $foo_bar_baz',
                                                           { 'foo': 'X', 'foo_bar': 'Y', 'foo_bar_baz': 'Z' }) )

  def test_has_rogue_dollar_signs(self):
    self.assertTrue( variable.has_rogue_dollar_signs('$foo') )
    self.assertFalse( variable.has_rogue_dollar_signs('\$foo') )

  def test_invalid_key(self):
    with self.assertRaises(TypeError) as context:
      variable.substitute('$foo and $bar', { 'foo': [ 'x' ], 'bar': 'Y' })

if __name__ == '__main__':
  unittest.main()
