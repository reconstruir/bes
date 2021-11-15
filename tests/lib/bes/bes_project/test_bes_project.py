#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_find import file_find
#from bes.python.pip_error import pip_error
from bes.python.python_exe import python_exe
#from bes.python.pip_installer_options import pip_installer_options
#from bes.python.pip_installer_tester import pip_installer_tester
from bes.bes_project.bes_project import bes_project
from bes.bes_project.bes_project_options import bes_project_options
from bes.python.python_testing import python_testing
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import raise_skip
from bes.testing.unit_test_skip import skip_if
from bes.version.semantic_version import semantic_version

class test_bes_project(unit_test):

  @classmethod
  def setUpClass(clazz):
    #raise_skip('Not ready')
    pass

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_invalid_package - no python3 found', warning = True)
  def xtest_install_invalid_package(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  #python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = bes_project(options = options)
    with self.assertRaises(pip_error) as ctx:
      project.install('somethingthatdoesntexistshaha')
    self.assertTrue( 'no matching distribution found for somethingthatdoesntexistshaha' in str(ctx.exception).lower() )

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_invalid_version - no python3 found', warning = True)
  def xtest_install_invalid_version(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = bes_project('kiwi', options = options)
    with self.assertRaises(pip_error) as ctx:
      project.install('pyinstaller', version = '666.666.666.666.666')
    print('ex={}'.format(str(ctx.exception).lower()))
    self.assertTrue( 'no matching distribution found for pyinstaller==666.666.666.666.666' in str(ctx.exception).lower() )
    
  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install_latest_version - no python3 found', warning = True)
  def test_ensure(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  debug = self.DEBUG)
    project = bes_project(options = options)
    version = python_exe.default_exe_version()
    requirements_content = '''\
# Requests
beautifulsoup4==4.9.3 # https://github.com/waylan/beautifulsoup
    '''
    requirements_tmp = self.make_temp_file(content = requirements_content)
    project.ensure([ str(version) ], requirements_tmp)
    self.assertEqual( [ version ], project.versions )
    
  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install - no python3 found', warning = True)
  def xtest_install_specific_version(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = bes_project('kiwi', options = options)
    project.install('pyinstaller', version = '3.5')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '3.5', rv.stdout.strip() )
    self.assertEqual( '3.5', project.version('pyinstaller') )
    self.assertTrue( project.needs_upgrade('pyinstaller') )

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install - no python3 found', warning = True)
  def xtest_upgrade(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    project = bes_project('kiwi', options = options)
    project.install('pyinstaller', version = '3.5')
    rv = project.call_program([ 'pyinstaller', '--version' ])
    old_version = semantic_version(project.version('pyinstaller'))
    self.assertEqual( '3.5', old_version )
    project.upgrade('pyinstaller')
    new_version = semantic_version(project.version('pyinstaller'))
    self.assertTrue( new_version > old_version )

  @skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_install - no python3 found', warning = True)
  def xtest_persistence(self):
    tmp_dir = self.make_temp_dir()
    options = bes_project_options(root_dir = tmp_dir,
                                  python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                  debug = self.DEBUG)
    p1 = bes_project('kiwi', options = options)
    p1.install('pyinstaller', version = '3.5')
    rv = p1.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '3.5', p1.version('pyinstaller') )
    p2 = bes_project('kiwi', options = options)
    p2.install('pyinstaller', version = '3.5')
    rv = p2.call_program([ 'pyinstaller', '--version' ])
    self.assertEqual( '3.5', p2.version('pyinstaller') )
    
if __name__ == '__main__':
  unit_test.main()
