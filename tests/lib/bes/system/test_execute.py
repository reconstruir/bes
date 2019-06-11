#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import skip_if
from bes.system.execute import execute
from bes.system.host import host

class test_execute(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.common/shell'

  def test_parse_args(self):
    self.assertEqual( [ 'echo', 'foo' ], execute.parse_args('echo foo') )
    self.assertEqual( [ 'echo', 'foo' ], execute.parse_args([ 'echo', 'foo' ]) )

  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success(self):
    bat = self.data_path('windows_batch_file_true.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_flat(self):
    bat = self.data_path('windows_batch_file_true.bat')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_shell(self):
    bat = self.data_path('windows_batch_file_true.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_flat_shell(self):
    bat = self.data_path('windows_batch_file_true.bat')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure(self):
    bat = self.data_path('windows_batch_file_false.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_flat(self):
    bat = self.data_path('windows_batch_file_false.bat')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_shell(self):
    bat = self.data_path('windows_batch_file_false.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  @skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_flat_shell(self):
    bat = self.data_path('windows_batch_file_false.bat')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = True, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  # FUCK
  @skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success(self):
    bat = self.data_path('unix_shell_script_true.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_flat(self):
    bat = self.data_path('unix_shell_script_true.sh')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_shell(self):
    bat = self.data_path('unix_shell_script_true.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_flat_shell(self):
    bat = self.data_path('unix_shell_script_true.sh')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure(self):
    bat = self.data_path('unix_shell_script_false.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  @skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_flat(self):
    bat = self.data_path('unix_shell_script_false.sh')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_shell(self):
    bat = self.data_path('unix_shell_script_false.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  @skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_flat_shell(self):
    bat = self.data_path('unix_shell_script_false.sh')
    cmd = '{} foo bar'.format(bat)
    rv = execute.execute(cmd, shell = True, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

if __name__ == "__main__":
  unit_test.main()
