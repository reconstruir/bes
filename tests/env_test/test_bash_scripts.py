#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path

from bes.system.execute import execute
from bes.system.host import host
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_bash_scripts(unit_test):

  @unit_test_function_skip.skip_if_not_unix()
  def test_bes_shell_sh(self):
    self.assertEqual( 0, self._run_test('test_bes_shell.sh') )
    
  def _run_test(self, script_name):
    print('here')
    script = path.join(path.dirname(__file__), script_name)
    env = self._make_env()
    rv = execute.execute(script,
                         shell = False,
                         stderr_to_stdout = True,
                         raise_error = False,
                         env = env,
                         quote = True)
    print(rv.stdout)
    return rv.exit_code
    
  @classmethod
  def _make_env(clazz):
    env = copy.deepcopy(os.environ)
    env['_BES_DEV_ROOT'] = clazz._root_dir()
    return env
    
  @classmethod
  def _this_dir(clazz):
    return path.join(path.dirname(__file__))
      
  @classmethod
  def _root_dir(clazz):
    return path.abspath(path.join(clazz._this_dir(), '../..'))

if __name__ == "__main__":
  unit_test.main()
