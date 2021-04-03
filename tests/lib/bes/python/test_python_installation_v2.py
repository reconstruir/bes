#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.python.python_installation_v2 import python_installation_v2
from bes.python.python_testing import python_testing
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if

class test_python_installation_v2(unit_test):

  @skip_if(not host.is_macos(), 'not macos')
  def test_macos_xcode_python_exe(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('3.8',
                                                                '19.2.3',
                                                                'xcode',
                                                                system = 'macos',
                                                                debug = self.DEBUG)

    piv = python_installation_v2(path.join(tmp_dir, 'bin/python3'), system = 'macos')
    self.assert_filename_equal( path.join(tmp_dir, 'bin/python3'), piv.python_exe )
    self.assert_filename_equal( path.join(tmp_dir, 'bin/pip3'), piv.pip_exe )
    self.assert_filename_equal( '3.8', piv.python_version )
    self.assert_filename_list_equal( [ path.join(tmp_dir, 'bin') ], piv.PATH )
    
    #self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    #self.assert_filename_list_equal( [ '/tmp/foo/lib/python/site-packages' ], piv.PYTHONPATH )

  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_python_38(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('3.8',
                                                                '19.2.3',
                                                                None,
                                                                system = 'windows',
                                                                debug = self.DEBUG)

    piv = python_installation_v2(path.join(tmp_dir, 'python.bat'), system = 'windows')
    self.assert_filename_equal( path.join(tmp_dir, 'python.bat'), piv.python_exe )
    self.assert_filename_equal( path.join(tmp_dir, 'Scripts', 'pip3.8.bat'), piv.pip_exe )
    self.assert_filename_equal( '3.8', piv.python_version )
    self.assert_filename_list_equal( [
      tmp_dir,
      path.join(tmp_dir, 'Scripts'),
    ], piv.PATH )

    #self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    #self.assert_filename_list_equal( [ '/tmp/foo/lib/python/site-packages' ], piv.PYTHONPATH )

  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_python_27(self):
    tmp_dir = python_testing.make_temp_fake_python_installation('2.7',
                                                                '20.3.4',
                                                                None,
                                                                system = 'windows',
                                                                debug = self.DEBUG)

    piv = python_installation_v2(path.join(tmp_dir, 'python.bat'), system = 'windows')
    self.assert_filename_equal( path.join(tmp_dir, 'python.bat'), piv.python_exe )
    self.assert_filename_equal( path.join(tmp_dir, 'Scripts', 'pip2.7.bat'), piv.pip_exe )
    self.assert_filename_equal( '2.7', piv.python_version )
    
  def xtest_macos_py27(self):
    piv = python_installation('/tmp/foo', '2.7', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip2.7', piv.pip_exe )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    self.assert_filename_list_equal( [ '/tmp/foo/lib/python/site-packages' ], piv.PYTHONPATH )

  def xtest_macos_py37(self):
    piv = python_installation('/tmp/foo', '3.7', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip3.7', piv.pip_exe )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    self.assert_filename_list_equal( [ '/tmp/foo/lib/python/site-packages' ], piv.PYTHONPATH )

  def xtest_macos_py38(self):
    piv = python_installation('/tmp/foo', '3.8', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip3.8', piv.pip_exe )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    self.assert_filename_list_equal( [ '/tmp/foo/lib/python/site-packages' ], piv.PYTHONPATH )

  def xtest_macos_py39(self):
    piv = python_installation('/tmp/foo', '3.9', system = 'macos')
    self.assert_filename_equal( '/tmp/foo/bin/pip3.9', piv.pip_exe )
    self.assert_filename_equal( '/tmp/foo/lib/python/site-packages', piv.site_packages_dir )
    self.assert_filename_list_equal( [ '/tmp/foo/lib/python/site-packages' ], piv.PYTHONPATH )

  def xtest_windows_py27(self):
    piv = python_installation(r'c:\tmp\foo', '2.7', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Scripts\pip2.7.exe', piv.pip_exe )
    self.assert_filename_equal( r'c:\tmp\foo\Python27\site-packages', piv.site_packages_dir )
    self.assert_filename_list_equal( [ r'c:\tmp\foo\Python27\site-packages' ], piv.PYTHONPATH )

  def xtest_windows_py37(self):
    piv = python_installation(r'c:\tmp\foo', '3.7', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Python37\Scripts\pip3.7.exe', piv.pip_exe )
    self.assert_filename_equal( r'c:\tmp\foo\Python37\site-packages', piv.site_packages_dir )
    self.assert_filename_list_equal( [ r'c:\tmp\foo\Python37\site-packages' ], piv.PYTHONPATH )

  def xtest_windows_py38(self):
    piv = python_installation(r'c:\tmp\foo', '3.8', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Python38\Scripts\pip3.8.exe', piv.pip_exe )
    self.assert_filename_equal( r'c:\tmp\foo\Python38\site-packages', piv.site_packages_dir )
    self.assert_filename_list_equal( [ r'c:\tmp\foo\Python38\site-packages' ], piv.PYTHONPATH )

  def xtest_windows_py39(self):
    piv = python_installation(r'c:\tmp\foo', '3.9', system = 'windows')
    self.assert_filename_equal( r'c:\tmp\foo\Python39\Scripts\pip3.9.exe', piv.pip_exe )
    self.assert_filename_equal( r'c:\tmp\foo\Python39\site-packages', piv.site_packages_dir )
    self.assert_filename_list_equal( [ r'c:\tmp\foo\Python39\site-packages' ], piv.PYTHONPATH )
    
if __name__ == '__main__':
  unit_test.main()
