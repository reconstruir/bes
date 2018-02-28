#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
import os.path as path
from bes.system import execute

class test_execute(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.common/shell'

  def test_true(self):
    script = self.data_path('shell_script_true.sh')
    rv = execute.execute(script)
    self.assertEqual( 0, rv.exit_code )

  def test_false(self):
    script = self.data_path('shell_script_false.sh')
    rv = execute.execute(script, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  def test_args(self):
    script = self.data_path('shell_script_true.sh')

    cmd = [
      script,
      'one',
      'two',
      'three',
    ]

    rv = execute.execute(cmd)

    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'one', 'two', 'three' ], rv.stdout.strip().split(' ') )

  def test_args_flat(self):
    script = self.data_path('shell_script_true.sh')

    cmd = '%s one two three' % (script)
    rv = execute.execute(cmd)

    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'one', 'two', 'three' ], rv.stdout.strip().split(' ') )

  def test_true_with_shell(self):
    script = self.data_path('shell_script_true.sh')
    rv = execute.execute(script, shell = True)
    self.assertEqual( 0, rv.exit_code )

  def test_false_with_shell(self):
    script = self.data_path('shell_script_false.sh')
    rv = execute.execute(script, raise_error = False, shell = True)
    self.assertEqual( 1, rv.exit_code )

  def test_args_with_shell(self):
    script = self.data_path('shell_script_true.sh')

    cmd = [
      script,
      'one',
      'two',
      'three',
    ]

    rv = execute.execute(cmd, shell = True)

    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'one', 'two', 'three' ], rv.stdout.strip().split(' ') )

  def test_args_flat_with_shell(self):
    script = self.data_path('shell_script_true.sh')

    cmd = '%s one two three' % (script)
    rv = execute.execute(cmd, shell = True)

    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'one', 'two', 'three' ], rv.stdout.strip().split(' ') )

if __name__ == "__main__":
  unit_test.main()
