#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.pip.pip_exe import pip_exe
from bes.pip.pip_installer import pip_installer
from bes.pip.pip_installer_options import pip_installer_options
from bes.python.python_exe import python_exe
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if

class test_pip_installer(unit_test):

  _PYTHON_27 = python_exe.find_version('2.7')
  _PYTHON_37 = python_exe.find_version('3.7')
  _PYTHON_38 = python_exe.find_version('3.8')
  _PYTHON_39 = python_exe.find_version('3.9')

  print('_PYTHON_27={}'.format(_PYTHON_27))
  print('_PYTHON_37={}'.format(_PYTHON_37))
  print('_PYTHON_38={}'.format(_PYTHON_38))
  print('_PYTHON_39={}'.format(_PYTHON_39))

  @skip_if(not _PYTHON_27, 'test_install_python_27 - python 3.7 not found', warning = True)
  def test_install_python_27(self):
    tmp_dir = self.make_temp_dir()
    options = pip_installer_options(root_dir = tmp_dir,
                                    python_exe = self._PYTHON_27,
                                    verbose = True,
                                    name = 'kiwi-27')
    installer = pip_installer(options)
    installer.install('19.2.3', False)
    #pexe = path.join(tmp_dir, 'kiwi-27', 'bin', 'pip2.7')
    #self.assertTrue( path.exists(pexe) )
    #self.assertEqual( '19.2.3', pip_exe.version(pexe) )

  @skip_if(not _PYTHON_37, 'test_install_python_37 - python 3.7 not found', warning = True)
  def test_install_python_37(self):
    print('running: test_install_python_37')

  @skip_if(not _PYTHON_38, 'test_install_python_38 - python 3.8 not found', warning = True)
  def test_install_python_38(self):
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
