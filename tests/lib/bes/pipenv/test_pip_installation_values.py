#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.pip.pip_installation_values import pip_installation_values
from bes.system.host import host
from bes.testing.unit_test import unit_test

class test_pip_installation_values(unit_test):

  def test_macos_py27(self):
    piv = pip_installation_values('/tmp/foo', '2.7', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip2.7', piv.exe )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.env['PYTHONPATH'] )
    self.assert_filename_equal( '/tmp/foo', piv.env['PYTHONUSERBASE'] )

  def test_macos_py37(self):
    piv = pip_installation_values('/tmp/foo', '3.7', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip3.7', piv.exe )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.env['PYTHONPATH'] )
    self.assert_filename_equal( '/tmp/foo', piv.env['PYTHONUSERBASE'] )

  def test_macos_py38(self):
    piv = pip_installation_values('/tmp/foo', '3.8', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip3.8', piv.exe )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.env['PYTHONPATH'] )
    self.assert_filename_equal( '/tmp/foo', piv.env['PYTHONUSERBASE'] )

  def test_macos_py39(self):
    piv = pip_installation_values('/tmp/foo', '3.9', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip3.9', piv.exe )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.env['PYTHONPATH'] )
    self.assert_filename_equal( '/tmp/foo', piv.env['PYTHONUSERBASE'] )

  def test_windows_py27(self):
    piv = pip_installation_values(r'c:\tmp\foo', '2.7', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Scripts\pip2.7.exe', piv.exe )
    self.assert_filename_equal( r'c:\tmp\foo\Python27\site-packages', piv.site_packages_dir )
    self.assert_filename_equal( r'c:\tmp\foo\Python27\site-packages', piv.env['PYTHONPATH'] )
    self.assert_filename_equal( r'c:\tmp\foo', piv.env['PYTHONUSERBASE'] )

  def test_windows_py37(self):
    piv = pip_installation_values(r'c:\tmp\foo', '3.7', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Python37\Scripts\pip3.7.exe', piv.exe )
    self.assert_filename_equal( r'c:\tmp\foo\Python37\site-packages', piv.site_packages_dir )
    self.assert_filename_equal( r'c:\tmp\foo\Python37\site-packages', piv.env['PYTHONPATH'] )
    self.assert_filename_equal( r'c:\tmp\foo', piv.env['PYTHONUSERBASE'] )

  def test_windows_py38(self):
    piv = pip_installation_values(r'c:\tmp\foo', '3.8', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Python38\Scripts\pip3.8.exe', piv.exe )
    self.assert_filename_equal( r'c:\tmp\foo\Python38\site-packages', piv.site_packages_dir )
    self.assert_filename_equal( r'c:\tmp\foo\Python38\site-packages', piv.env['PYTHONPATH'] )
    self.assert_filename_equal( r'c:\tmp\foo', piv.env['PYTHONUSERBASE'] )

  def test_windows_py39(self):
    piv = pip_installation_values(r'c:\tmp\foo', '3.9', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Python39\Scripts\pip3.9.exe', piv.exe )
    self.assert_filename_equal( r'c:\tmp\foo\Python39\site-packages', piv.site_packages_dir )
    self.assert_filename_equal( r'c:\tmp\foo\Python39\site-packages', piv.env['PYTHONPATH'] )
    self.assert_filename_equal( r'c:\tmp\foo', piv.env['PYTHONUSERBASE'] )
    
if __name__ == '__main__':
  unit_test.main()
