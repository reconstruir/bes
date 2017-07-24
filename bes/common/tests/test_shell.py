#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.common import Shell

class test_Shell(unittest.TestCase):

  TEST_DATA_DIR = path.abspath(path.join(path.dirname(__file__), 'test_data/shell'))

  def test_true(self):
    script = path.join(self.TEST_DATA_DIR, 'shell_script_true.sh')
    rv = Shell.execute(script)
    self.assertEqual( 0, rv.exit_code )

  def test_false(self):
    script = path.join(self.TEST_DATA_DIR, 'shell_script_false.sh')
    rv = Shell.execute(script, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  def test_args(self):
    script = path.join(self.TEST_DATA_DIR, 'shell_script_true.sh')

    cmd = [
      script,
      'one',
      'two',
      'three',
    ]

    rv = Shell.execute(cmd)

    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'one', 'two', 'three' ], rv.stdout.strip().split(' ') )

  def test_args_flat(self):
    script = path.join(self.TEST_DATA_DIR, 'shell_script_true.sh')

    cmd = '%s one two three' % (script)
    rv = Shell.execute(cmd)

    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'one', 'two', 'three' ], rv.stdout.strip().split(' ') )

  def test_true_with_shell(self):
    script = path.join(self.TEST_DATA_DIR, 'shell_script_true.sh')
    rv = Shell.execute(script, shell = True)
    self.assertEqual( 0, rv.exit_code )

  def test_false_with_shell(self):
    script = path.join(self.TEST_DATA_DIR, 'shell_script_false.sh')
    rv = Shell.execute(script, raise_error = False, shell = True)
    self.assertEqual( 1, rv.exit_code )

  def test_args_with_shell(self):
    script = path.join(self.TEST_DATA_DIR, 'shell_script_true.sh')

    cmd = [
      script,
      'one',
      'two',
      'three',
    ]

    rv = Shell.execute(cmd, shell = True)

    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'one', 'two', 'three' ], rv.stdout.strip().split(' ') )

  def test_args_flat_with_shell(self):
    script = path.join(self.TEST_DATA_DIR, 'shell_script_true.sh')

    cmd = '%s one two three' % (script)
    rv = Shell.execute(cmd, shell = True)

    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( [ 'one', 'two', 'three' ], rv.stdout.strip().split(' ') )

if __name__ == '__main__':
  unittest.main()
