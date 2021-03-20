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
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if

class test_pip_installer(unit_test):

  # The python 3.8 that comes with xcode is very non standard
  # crapping all kinds of droppings in non standard places such
  # as ~/Library/Caches and the pip that comes with it does not
  # respected --no-cache-dir so dont ever user it
  _EXCLUDE_SOURCES = ( 'xcode', )
  
  _PYTHON_27 = bes_python_exe.find_version('2.7', exclude_sources = _EXCLUDE_SOURCES)
  _PYTHON_37 = bes_python_exe.find_version('3.7', exclude_sources = _EXCLUDE_SOURCES)
  _PYTHON_38 = bes_python_exe.find_version('3.8', exclude_sources = _EXCLUDE_SOURCES)
  _PYTHON_39 = bes_python_exe.find_version('3.9', exclude_sources = _EXCLUDE_SOURCES)

  print('_PYTHON_27={}'.format(_PYTHON_27))
  print('_PYTHON_37={}'.format(_PYTHON_37))
  print('_PYTHON_38={}'.format(_PYTHON_38))
  print('_PYTHON_39={}'.format(_PYTHON_39))

  @skip_if(not _PYTHON_27, 'test_install_python_27 - python 2.7 not found', warning = True)
  def test_install_python_27(self):
    tester = self._make_tester(self._PYTHON_27, 'kiwi-27')
    self.assertFalse( path.exists(tester.pip_exe) )
    tester.installer.install('19.2.3', False)
    self.assertTrue( path.exists(tester.pip_exe) )
    self.assertEqual( '19.2.3', pip_exe.version(tester.pip_exe) )

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
    
  @skip_if(not _PYTHON_37, 'test_install_python_37 - python 3.7 not found', warning = True)
  def test_install_python_37(self):
    print('running: test_install_python_37')

  @skip_if(not _PYTHON_38, 'test_install_python_38 - python 3.8 not found', warning = True)
  def test_install_python_38(self):
    from bes.system.env_override import env_override
    e = { 'PYTHONUSERBASE': '/tmp/a' }
    with env_override(env = e) as env: #{ 'PYTHONNOUSERSITE': 'tmp/caca_de_vaca' }) as env:
      tmp_dir = self.make_temp_dir()
      options = pip_installer_options(root_dir = tmp_dir,
                                      python_exe = self._PYTHON_38,
                                      verbose = True,
                                      name = 'apple-38')
      installer = pip_installer(options)
      installer.install('19.2.3', False)
      files = file_find.find(tmp_dir)
      for f in files:
        print(f)

  @skip_if(not _PYTHON_39, 'test_install_python_39 - python 3.9 not found', warning = True)
  def test_install_python_39(self):
    print('running: test_install_python_39')
    
if __name__ == '__main__':
  unit_test.main()
