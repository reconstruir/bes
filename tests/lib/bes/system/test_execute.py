#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common.string_util import string_util
from bes.system.execute import execute
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_execute(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.common/shell'

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success(self):
    bat = self.data_path('windows_batch_file_true.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_flat(self):
    bat = self.data_path('windows_batch_file_true.bat')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_shell(self):
    bat = self.data_path('windows_batch_file_true.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_flat_shell(self):
    bat = self.data_path('windows_batch_file_true.bat')
    cmd = '"{}" foo bar'.format(bat)
    rv = execute.execute(cmd, shell = True, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure(self):
    bat = self.data_path('windows_batch_file_false.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_flat(self):
    bat = self.data_path('windows_batch_file_false.bat')
    cmd = '"{}" foo bar'.format(bat)
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_shell(self):
    bat = self.data_path('windows_batch_file_false.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_flat_shell(self):
    bat = self.data_path('windows_batch_file_false.bat')
    cmd = '"{}" foo bar'.format(bat)
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success(self):
    bat = self.data_path('unix_shell_script_true.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_flat(self):
    bat = self.data_path('unix_shell_script_true.sh')
    cmd = '"{}" foo bar'.format(bat)
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_shell(self):
    bat = self.data_path('unix_shell_script_true.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_flat_shell(self):
    bat = self.data_path('unix_shell_script_true.sh')
    cmd = '"{}" foo bar'.format(bat)
    rv = execute.execute(cmd, shell = True, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure(self):
    bat = self.data_path('unix_shell_script_false.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_flat(self):
    bat = self.data_path('unix_shell_script_false.sh')
    cmd = '"{}" foo bar'.format(bat)
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_shell(self):
    bat = self.data_path('unix_shell_script_false.sh')
    cmd = [ '"{}"'.format(bat), 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_flat_shell(self):
    bat = self.data_path('unix_shell_script_false.sh')
    cmd = '"{}" foo bar'.format(bat)
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  def test_python_script_success(self):
    content = '''\
import sys
print('success:{}'.format(sys.argv[1]))
raise SystemExit(0)
'''
    script = self.make_temp_file(content = content, perm = 0o0755, suffix = '.py')
    cmd = [ script, 'foo' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'success:foo', rv.stdout.strip() )

  def test_python_script_failure(self):
    content = '''\
import sys
print('failure:{}'.format(sys.argv[1]))
raise SystemExit(1)
'''
    script = self.make_temp_file(content = content, perm = 0o0755, suffix = '.py')
    cmd = [ script, 'foo' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  def test_python_script_uppercase_extension(self):
    content = '''\
import sys
print('success:{}'.format(sys.argv[1]))
raise SystemExit(0)
'''
    script = self.make_temp_file(content = content, perm = 0o0755, suffix = '.PY')
    cmd = [ script, 'foo' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'success:foo', rv.stdout.strip() )
    
if __name__ == '__main__':
  unit_test.main()
