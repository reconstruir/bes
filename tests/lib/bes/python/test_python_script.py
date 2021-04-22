#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.python.python_error import python_error
from bes.python.python_script import python_script
from bes.python.python_testing import python_testing
from bes.system.host import host
from bes.testing.unit_test import unit_test

class test_python_script(unit_test):

  def test_run_script_success(self):
    script = r'''
import sys
sys.stdout.write('kiwi\n')
sys.stdout.flush()
raise SystemExit(0)
'''
    rv = python_script.run_script(python_testing._PYTHONS.ANY_PYTHON, script, [])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'kiwi', rv.output.strip() )

  def test_run_script_failure(self):
    script = r'''
import sys
sys.stdout.write('lemon\n')
sys.stdout.flush()
raise SystemExit(42)
'''
    rv = python_script.run_script(python_testing._PYTHONS.ANY_PYTHON, script, [])
    self.assertEqual( 42, rv.exit_code )
    self.assertEqual( 'lemon', rv.output.strip() )

  def test_run_script_stderr(self):
    script = r'''
import sys
sys.stderr.write('kiwi\n')
sys.stderr.flush()
raise SystemExit(0)
'''
    rv = python_script.run_script(python_testing._PYTHONS.ANY_PYTHON, script, [])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'kiwi', rv.output.strip() )
    
if __name__ == '__main__':
  unit_test.main()
