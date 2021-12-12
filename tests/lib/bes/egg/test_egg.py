#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from os import path

from bes.testing.unit_test import unit_test
from bes.testing.egg_unit_test import egg_unit_test

from bes.python.pip_project import pip_project
from bes.python.pip_project_options import pip_project_options
from bes.python.python_testing import python_testing
from bes.fs.file_util import file_util
from bes.system.execute import execute
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.egg.egg import egg
from bes.egg.egg_options import egg_options

class test_egg(unit_test):

  @unit_test_function_skip.skip_if(not python_testing._PYTHONS.ANY_PYTHON3, 'test_make_from_address - no python3 found', warning = True)
  def test_make_from_address(self):
    tmp_dir = self.make_temp_dir(suffix = '.test_make_from_address', )
    venvs_dir = path.join(tmp_dir, 'venvs')
    pp_options = pip_project_options(root_dir = venvs_dir,
                                     python_exe = python_testing._PYTHONS.ANY_PYTHON3,
                                     debug = self.DEBUG)
    project = pip_project(options = pp_options)
    project.install('setuptools')

    for p in project.PYTHONPATH:
      sys.path.insert(0, p)
    
    options = egg_options(setup_filename = 'setup.py',
                          version_filename = 'lib/bes/ver.py',
                          verbose = self.DEBUG,
                          debug = self.DEBUG)
    result = egg.make_from_address('https://github.com/reconstruir/bes.git', '1.2.62',
                                   options = options,
                                   python_exe = project.python_exe)
    print('result={}'.format(result))

if __name__ == '__main__':
  unit_test.main()
