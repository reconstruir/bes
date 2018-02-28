#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import copy, os, os.path as path
from bes.testing.unit_test import unit_test
from bes.system import execute

class test_bash_scripts(unit_test):

  def test_bes_framework_sh(self):
    self.assertEqual( 0, self._run_test('test_bes_framework.sh') )
    
  def test_bes_path_sh(self):
    self.assertEqual( 0, self._run_test('test_bes_path.sh') )
    
  def _run_test(self, script_name):
    script = path.join(path.dirname(__file__), script_name)
    print("python: running: %s" % (script))
    env = self._make_env()
    rv = execute.execute(script,
                         shell = False,
                         stderr_to_stdout = True,
                         raise_error = False,
                         env = env)
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
