#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.build.build_arch import build_arch as BA
from bes.build.build_level import build_level as BL
from bes.build.build_system import build_system as BS
from bes.build.build_target import build_target as BT

class test_build_target(unit_test):

  def test_build_path(self):
    self.assertEqual( 'macos-10.10/x86_64/release', BT('macos', '', '10', '10', 'x86_64', 'release').build_path )
    self.assertEqual( 'macos-10/x86_64/release', BT('macos', '', '10', None, 'x86_64', 'release').build_path )
    self.assertEqual( 'linux-ubuntu-18/x86_64/release', BT('linux', 'ubuntu', '18', None, 'x86_64', 'release').build_path )
    self.assertEqual( 'ios-12/arm64-armv7/release', BT('ios', '', '12', None,  'armv7,arm64', 'release').build_path )
    self.assertEqual( 'ios-12/arm64-armv7/debug', BT('ios', '', '12', None, 'armv7,arm64', 'debug').build_path )
    self.assertEqual( 'ios-12/arm64/release', BT('ios', '', '12', None, 'arm64', 'release').build_path )
    self.assertEqual( 'ios-12/arm64/debug', BT('ios', '', '12', None, 'arm64', 'debug').build_path )
    self.assertEqual( 'macos/x86_64/release', BT('macos', '', '', None, 'x86_64', 'release').build_path )
    self.assertEqual( 'linux-ubuntu/x86_64/release', BT('linux', 'ubuntu', '', None, 'x86_64', 'release').build_path )
    self.assertEqual( 'linux/x86_64/release', BT('linux', 'none', '', None, 'x86_64', 'release').build_path )
    
  def test_parse_path(self):
    self.assertEqual( BT('macos', None, '10', None, 'x86_64', 'release'), BT.parse_path('macos-10/x86_64/release') )
    self.assertEqual( BT('macos', None, '10', '10', 'x86_64', 'release'), BT.parse_path('macos-10.10/x86_64/release') )
    self.assertEqual( BT('linux', 'ubuntu', '18', None, 'x86_64', 'release'), BT.parse_path('linux-ubuntu-18/x86_64/release') )
    self.assertEqual( BT('linux', None, None, None, 'x86_64', 'release'), BT.parse_path('linux/x86_64/release') )
    self.assertEqual( BT('ios', None, '12', None, 'armv7,arm64', 'release'), BT.parse_path('ios-12/arm64-armv7/release') )
    self.assertEqual( BT('ios', None, '12', None, 'armv7,arm64', 'debug'), BT.parse_path('ios-12/arm64-armv7/debug') )
    self.assertEqual( BT('macos', None, '10', None, 'x86_64', 'debug'), BT.parse_path('macos-10/x86_64/debug') )
    self.assertEqual( BT('macos', None, '10', None, 'x86_64', 'release'), BT.parse_path('macos-10/x86_64') )
    self.assertEqual( BT('linux', None, None, None, 'x86_64', 'release'), BT.parse_path('linux/x86_64') )
    self.assertEqual( BT('linux', None, None, None, 'x86_64', 'release'), BT.parse_path('linux/x86_64/release') )
    self.assertEqual( BT('linux', None, None, None, 'x86_64', 'debug'), BT.parse_path('linux/x86_64/debug') )
    
  def test_parse_expression(self):
    F = self._parse_exp
    self.assertTrue( F('macos-10.10/x86_64/release', '${system} == MACOS and ${level} == RELEASE') )
    self.assertFalse( F('macos-10.10/x86_64/release', '${system} == MACOS and ${level} != RELEASE') )
    self.assertTrue( F('linux-raspbian-9/x86_64/release', '${system} == LINUX and ${distro} == RASPBIAN') )
    self.assertFalse( F('linux-raspbian-9/x86_64/release', '${system} == MACOS or (${system} == LINUX and ${distro} != RASPBIAN)') )
    self.assertTrue( F('macos-10.10/x86_64/release', '${system} == MACOS or (${system} == LINUX and ${distro} != RASPBIAN)') )
    self.assertTrue( F('macos-10.10/x86_64/debug', '${system} == MACOS or (${system} == LINUX and ${distro} != RASPBIAN)') )
    self.assertTrue( F('linux-ubuntu-18/x86_64/release', '${system} == MACOS or (${system} == LINUX and ${distro} != RASPBIAN)') )
    self.assertTrue( F('linux-ubuntu-18/x86_64/debug', '${system} == MACOS or (${system} == LINUX and ${distro} != RASPBIAN)') )

  def test_clone(self):
    p = BT.parse_path
    self.assertEqual( 'macos-10.10/x86_64/release',
                      p('macos-10.10/x86_64/release').clone().build_path )
    self.assertEqual( 'macos-10.10/x86_64/debug',
                      p('macos-10.10/x86_64/release').clone({ 'level': 'debug' }).build_path )
    self.assertEqual( 'macos-10.10/i386/release',
                      p('macos-10.10/x86_64/release').clone({ 'arch': 'i386' }).build_path )
    self.assertEqual( 'macos-10.10/i386/debug',
                      p('macos-10.10/x86_64/release').clone({ 'level': 'debug', 'arch': 'i386' }).build_path )

  def _parse_exp(self, bt_path, exp):
    return BT.parse_path(bt_path).parse_expression(exp)

  def test_make_build_path(self):
    bt = BT('macos', '', '10', '10', 'x86_64', 'release')
    self.assertEqual( 'macos-10.10;x86_64;release', bt.make_build_path(delimiter = ';') )
    self.assertEqual( 'macos-10.10/x86_64', bt.make_build_path(include_level = False) )
    self.assertEqual( 'macos-10/x86_64', bt.make_build_path(include_level = False, include_minor_version = False) )
    self.assertEqual( 'macos-10', bt.make_build_path(include_level = False, include_minor_version = False, include_arch = False) )

  def _match_text(self, what, text):
    return BT.parse_path(what).match_text(text)
    
  def test_match_text(self):
    self.assertTrue( self._match_text('macos-10.10/x86_64/release', 'macos') )
    self.assertTrue( self._match_text('macos-10.10/x86_64/release', 'macos-10') )
    self.assertTrue( self._match_text('macos-10.10/x86_64/release', 'macos-10.10') )
    self.assertTrue( self._match_text('macos-10.10/x86_64/release', 'macos-10.10/x86_64') )
    self.assertTrue( self._match_text('macos-10.10/x86_64/release', 'macos-10.10/x86_64/release') )

    self.assertFalse( self._match_text('macos-10.10/x86_64/release', 'macos-10.20') )
    self.assertFalse( self._match_text('macos-10.10/x86_64/release', 'windows-10.0') )
    self.assertFalse( self._match_text('macos-10.10/x86_64/release', 'macos-10.10/x86_64/debug') )

    self.assertTrue( self._match_text('macos-10.10/x86_64/release', '*') )
    self.assertTrue( self._match_text('macos-10.10/x86_64/release', 'macos-*/x86_64/*') )
    self.assertTrue( self._match_text('macos-10.10/x86_64/debug', 'macos-*/x86_64/*') )
    
  def test__parse_version(self):
    self.assertEqual( ( '10', '10' ), BT._parse_version('10.10', None) )
    self.assertEqual( ( '*', '*' ), BT._parse_version('*.*', None) )
    self.assertEqual( ( '10', None ), BT._parse_version('10', None) )
    self.assertEqual( ( None, None ), BT._parse_version('', None) )
    self.assertEqual( ( None, None ), BT._parse_version(None, None) )

  def test__parse_with_default_value(self):
    self.assertEqual( ( '10', '10' ), BT._parse_version('10.10', 'foo') )
    self.assertEqual( ( '*', '*' ), BT._parse_version('*.*', 'foo') )
    self.assertEqual( ( '10', 'foo' ), BT._parse_version('10', 'foo') )
    self.assertEqual( ( 'foo', 'foo' ), BT._parse_version('', 'foo') )
    self.assertEqual( ( 'foo', 'foo' ), BT._parse_version(None, 'foo') )
    
if __name__ == '__main__':
  unit_test.main()
