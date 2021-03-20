#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.pip.pip_exe import pip_exe
from bes.pip.pip_installer import pip_installer
from bes.pip.pip_installer_options import pip_installer_options
from bes.python.python_exe import python_exe as bes_python_exe
from bes.python.python_version import python_version as bes_python_version
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if
from bes.version.software_version import software_version

class test_pip_installer(unit_test):

  # The python 3.8 that comes with xcode is very non standard
  # crapping all kinds of droppings in non standard places such
  # as ~/Library/Caches even though the --no-cache-dir was given
  # so never use them for tests since they create side effects
  _EXCLUDE_SOURCES = ( 'xcode', )
  
  _PYTHON_27 = bes_python_exe.find_version('2.7', exclude_sources = _EXCLUDE_SOURCES)
  _PYTHON_37 = bes_python_exe.find_version('3.7', exclude_sources = _EXCLUDE_SOURCES)
  _PYTHON_38 = bes_python_exe.find_version('3.8', exclude_sources = _EXCLUDE_SOURCES)
  _PYTHON_39 = bes_python_exe.find_version('3.9', exclude_sources = _EXCLUDE_SOURCES)

  _ALL_PYTHONS = [ p for p in [ _PYTHON_27, _PYTHON_37, _PYTHON_38, _PYTHON_39 ] if p ]
  _ANY_PYTHON2 = next(iter([ p for p in _ALL_PYTHONS if bes_python_exe.major_version(p) == 2]), None)
  _ANY_PYTHON3 = next(iter([ p for p in _ALL_PYTHONS if bes_python_exe.major_version(p) == 3]), None)

  #print('_ALL_PYTHONS: {}'.format(_ALL_PYTHONS))
  #print('_ANY_PYTHON2: {}'.format(_ANY_PYTHON2))
  #print('_ANY_PYTHON3: {}'.format(_ANY_PYTHON3))
  #raise SystemExit(1)
  
  @skip_if(not _PYTHON_27, 'test_install_python_27 - python 2.7 not found', warning = True)
  def test_install_python_27(self):
    tester = self._make_tester(self._PYTHON_27, 'test')
    self.assertFalse( path.exists(tester.pip_exe) )
    tester.installer.install('latest', False)
    self.assertTrue( path.exists(tester.pip_exe) )
    self.assertEqual( 1, software_version.compare(tester.installer.pip_version(), '19.0.0') )

  @skip_if(not _PYTHON_37, 'test_install_python_37 - python 3.7 not found', warning = True)
  def test_install_python_37(self):
    tester = self._make_tester(self._PYTHON_37, 'test')
    self.assertFalse( path.exists(tester.pip_exe) )
    tester.installer.install('latest', False)
    self.assertTrue( path.exists(tester.pip_exe) )
    self.assertEqual( 1, software_version.compare(tester.installer.pip_version(), '19.0.0') )

  @skip_if(not _PYTHON_38, 'test_install_python_38 - python 3.8 not found', warning = True)
  def test_install_python_38(self):
    tester = self._make_tester(self._PYTHON_38, 'test')
    self.assertFalse( path.exists(tester.pip_exe) )
    tester.installer.install('latest', False)
    self.assertTrue( path.exists(tester.pip_exe) )
    self.assertEqual( 1, software_version.compare(tester.installer.pip_version(), '19.0.0') )

  @skip_if(not _PYTHON_39, 'test_install_python_39 - python 3.9 not found', warning = True)
  def test_install_python_39(self):
    tester = self._make_tester(self._PYTHON_39, 'test')
    self.assertFalse( path.exists(tester.pip_exe) )
    tester.installer.install('latest', False)
    self.assertTrue( path.exists(tester.pip_exe) )
    self.assertEqual( 1, software_version.compare(tester.installer.pip_version(), '19.0.0') )

  @skip_if(not _ANY_PYTHON3, 'test_uninstall_python3 - python 3 not found', warning = True)
  def test_uninstall_python3(self):
    tester = self._make_tester(self._ANY_PYTHON3, 'test')
    tester.installer.install('latest', False)
    self.assertTrue( tester.installer.is_installed() )
    tester.installer.uninstall()
    self.assertFalse( tester.installer.is_installed() )

  @skip_if(not _ANY_PYTHON3, 'test_install_specific_version - python 3 not found', warning = True)
  def test_install_specific_version(self):
    tester = self._make_tester(self._ANY_PYTHON3, 'test')
    tester.installer.install('19.2.3', False)
    self.assertEqual( '19.2.3', tester.installer.pip_version() )
    
  _tester = namedtuple('_tester', 'name, tmp_dir, installer, python_exe, python_version, pip_exe')
  @classmethod
  def _make_tester(clazz, python_exe, name):
    tmp_dir = clazz.make_temp_dir()
    options = pip_installer_options(root_dir = tmp_dir,
                                    python_exe = python_exe,
                                    verbose = True,
                                    name = name)
    installer = pip_installer(options)
    python_exe_version = bes_python_exe.version(python_exe)
    pip_exe_basename = 'pip{}'.format(python_exe_version)
    pexe = path.join(tmp_dir, name, 'bin', pip_exe_basename)
    return clazz._tester(name,
                         tmp_dir,
                         installer,
                         python_exe,
                         python_exe_version,
                         pexe)
    
if __name__ == '__main__':
  unit_test.main()
