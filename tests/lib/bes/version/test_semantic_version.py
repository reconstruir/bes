#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.system.check import check

from bes.version.semantic_version import semantic_version
from bes.version.semantic_version_error import semantic_version_error

class test_semantic_version(unit_test):

  def test__tokens_to_string(self):
    self.assertEqual( '1.0.0', semantic_version._tokens_to_string(semantic_version('1.0.0')._tokens) )

  def test__tokens_to_string_different_delimiters(self):
    self.assertEqual( '1.0.0-4', semantic_version._tokens_to_string(semantic_version('1.0.0-4')._tokens) )

  def test__tokens_to_string_mixture(self):
    self.assertEqual( 'rel/foo/1.2.3-4', semantic_version._tokens_to_string(semantic_version('rel/foo/1.2.3-4')._tokens) )

  def test__tokens_to_string_empty_string(self):
    self.assertEqual( '', semantic_version._tokens_to_string(semantic_version('')._tokens) )

  def test__part_tokens(self):
    self.assertEqual( '1234', semantic_version._tokens_to_string(semantic_version('rel/foo/1.2.3-4')._part_tokens) )

  def test__part_tokens_with_gaps(self):
    self.assertEqual( '1234', semantic_version._tokens_to_string(semantic_version('rel/v2/1.2.3-4')._part_tokens) )

  def test_change_part_major(self):
    self.assertEqual( 'rel/v2/2.2.3', str(semantic_version('rel/v2/1.2.3').change_part(0, 1)) )

  def test_change_part_minor(self):
    self.assertEqual( 'rel/v2/1.3.3', str(semantic_version('rel/v2/1.2.3').change_part(1, 1)) )

  def test_change_part_revision(self):
    self.assertEqual( 'rel/v2/1.2.4', str(semantic_version('rel/v2/1.2.3').change_part(2, 1)) )
    
  def test_change_part_invalid_part(self):
    with self.assertRaises(semantic_version_error) as ctx:
      semantic_version('rel/v2/1.2.3').change_part(4, 1)

  def test_compare(self):
    self.assertEqual( -1, semantic_version.compare('1.2.3', '1.2.4') )
    self.assertEqual(  0, semantic_version.compare('1.2.3', '1.2.3') )
    self.assertEqual(  1, semantic_version.compare('1.2.4', '1.2.3') )
    self.assertEqual( -1, semantic_version.compare('1.2.8', '1.2.9') )
    self.assertEqual( -1, semantic_version.compare('1.2.10', '1.2.11') )
    self.assertEqual( -1, semantic_version.compare('1.2.9', '1.2.10') )
    self.assertEqual( -1, semantic_version.compare('3.0.4', '3.3') )
    
    self.assertEqual(  1, semantic_version.compare('1:1.2.3', '1.2.4') )
    self.assertEqual( -1, semantic_version.compare('0:1.2.3', '1.2.4') )
    self.assertEqual( -1, semantic_version.compare('0:1.2.3', '0:1.2.3-1') )
    self.assertEqual(  1, semantic_version.compare('0:1.2.3-3', '0:1.2.3-2') )

    self.assertEqual(  1, semantic_version.compare('1.2.3', '1.2-3') )
    self.assertEqual( -1, semantic_version.compare('1.2-3', '1.2.3') )

  def test_compare_with_fluff(self):
    self.assertEqual( 0, semantic_version.compare('rel/v2/foo-1.2.3', 'rel/v2/foo-1.2.3') )

  def test_part_value(self):
    self.assertEqual( 1, semantic_version('rel/v2/1.2.3').part_value(0) )
    self.assertEqual( 2, semantic_version('rel/v2/1.2.3').part_value(1) )
    self.assertEqual( 3, semantic_version('rel/v2/1.2.3').part_value(2) )

  def test_set_part(self):
    self.assertEqual( 'rel/v2/6.2.3', str(semantic_version('rel/v2/1.2.3').set_part(0, 6)) )
    self.assertEqual( 'rel/v2/1.6.3', str(semantic_version('rel/v2/1.2.3').set_part(1, 6)) )
    self.assertEqual( 'rel/v2/1.2.6', str(semantic_version('rel/v2/1.2.3').set_part(2, 6)) )

  def test_parts(self):
    self.assertEqual( ( 1, 2, 3 ), semantic_version('rel/v2/1.2.3').parts )
    self.assertEqual( ( 1, 2 ), semantic_version('1.2').parts )
    self.assertEqual( ( 1, ), semantic_version('1').parts )

  def test___getitem__(self):
    self.assertEqual( 1, semantic_version('rel/v2/1.2.3')[0] )
    self.assertEqual( 2, semantic_version('rel/v2/1.2.3')[1] )
    self.assertEqual( 3, semantic_version('rel/v2/1.2.3')[2] )

  def test___eq__(self):
    self.assertTrue( semantic_version('rel/v2/1.2.1') == semantic_version('rel/v2/1.2.1') )
    self.assertFalse( semantic_version('sel/v2/1.2.1') == semantic_version('rel/v2/1.2.1') )
    self.assertFalse( semantic_version('rels/v2/1.2.1') == semantic_version('rel/v2/1.2.1') )

  def test___ne__(self):
    self.assertFalse( semantic_version('rel/v2/1.2.1') != semantic_version('rel/v2/1.2.1') )
    self.assertTrue( semantic_version('sel/v2/1.2.1') != semantic_version('rel/v2/1.2.1') )
    self.assertTrue( semantic_version('rels/v2/1.2.1') != semantic_version('rel/v2/1.2.1') )
    
  def test___lt__(self):
    self.assertTrue( semantic_version('rel/v2/1.2.1') < semantic_version('rel/v2/1.2.10') )
    self.assertFalse( semantic_version('rel/v2/1.2.1') < semantic_version('rel/v2/1.2.1') )
    self.assertFalse( semantic_version('rel/v2/1.2.10') < semantic_version('rel/v2/1.2.1') )

  def test___le__(self):
    self.assertTrue( semantic_version('rel/v2/1.2.1') <= semantic_version('rel/v2/1.2.10') )
    self.assertTrue( semantic_version('rel/v2/1.2.1') <= semantic_version('rel/v2/1.2.1') )
    self.assertFalse( semantic_version('rel/v2/1.2.10') <= semantic_version('rel/v2/1.2.1') )

  def test___gt__(self):
    self.assertFalse( semantic_version('rel/v2/1.2.1') > semantic_version('rel/v2/1.2.10') )
    self.assertFalse( semantic_version('rel/v2/1.2.1') > semantic_version('rel/v2/1.2.1') )
    self.assertTrue( semantic_version('rel/v2/1.2.10') > semantic_version('rel/v2/1.2.1') )

  def test___ge__(self):
    self.assertFalse( semantic_version('rel/v2/1.2.1') >= semantic_version('rel/v2/1.2.10') )
    self.assertTrue( semantic_version('rel/v2/1.2.1') >= semantic_version('rel/v2/1.2.1') )
    self.assertTrue( semantic_version('rel/v2/1.2.10') >= semantic_version('rel/v2/1.2.1') )
    self.assertFalse( semantic_version('rel/v2/1.2.1') >= 'rel/v2/1.2.10' )
    self.assertTrue( semantic_version('rel/v2/1.2.1') >= 'rel/v2/1.2.1' )
    self.assertTrue( semantic_version('rel/v2/1.2.10') >= 'rel/v2/1.2.1' )
    self.assertFalse( 'rel/v2/1.2.1' >= semantic_version('rel/v2/1.2.10') )
    self.assertTrue( 'rel/v2/1.2.1' >= semantic_version('rel/v2/1.2.1') )
    self.assertTrue( 'rel/v2/1.2.10' >= semantic_version('rel/v2/1.2.1') )

  def test_has_only_semantic_tokens(self):
    self.assertTrue( semantic_version('1.2.3').has_only_semantic_tokens )
    self.assertTrue( semantic_version('1.2;3').has_only_semantic_tokens )
    self.assertTrue( semantic_version('1.2-3').has_only_semantic_tokens )
    self.assertFalse( semantic_version('1.2.alpha').has_only_semantic_tokens )
    self.assertFalse( semantic_version('1.2.3a').has_only_semantic_tokens )
    self.assertFalse( semantic_version('amazing/1.2.3').has_only_semantic_tokens )

  def test_check_with_cast(self):
    self.assertEqual( semantic_version('1.2.3'), check.check_semantic_version('1.2.3') )

  def test__parse_clause(self):
    f = semantic_version._parse_clause
    self.assertEqual( ( '<', '3.8' ), f('< 3.8') )
    self.assertEqual( ( '>', '3.8' ), f('> 3.8') )
    self.assertEqual( ( '==', '3.8' ), f('== 3.8') )
    self.assertEqual( ( '!=', '3.8' ), f('!= 3.8') )
    self.assertEqual( ( '<=', '3.8' ), f('<= 3.8') )
    self.assertEqual( ( '>=', '3.8' ), f('>= 3.8') )

  def test__parse_clause_invalid_operator(self):
    f = semantic_version._parse_clause
    with self.assertRaises(ValueError) as _:
      f('!! 3.8')

  def test__parse_clause_invalid_version(self):
    f = semantic_version._parse_clause
    with self.assertRaises(ValueError) as _:
      f('== 3.8alpha')

  def test__match_clause(self):
    self.assertEqual( True, semantic_version('3.9').match_clause('== 3.9') )
    self.assertEqual( False, semantic_version('3.9').match_clause('!= 3.9') )
    self.assertEqual( False, semantic_version('3.9').match_clause('< 3.9') )
    self.assertEqual( True, semantic_version('3.9').match_clause('> 3.8') )
    self.assertEqual( True, semantic_version('3.9').match_clause('<= 3.9') )
    self.assertEqual( True, semantic_version('3.9').match_clause('>= 3.8') )
      
if __name__ == '__main__':
  unit_test.main()
