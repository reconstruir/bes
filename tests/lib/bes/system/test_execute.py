#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common.string_util import string_util
from bes.system.execute import execute
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_execute(unit_test):

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success(self):
    script = '''\
@echo off
echo %*
exit 0
'''
    bat = self.make_temp_file(content = script, suffix = '.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_flat(self):
    script = '''\
@echo off
echo %*
exit 0
'''
    bat = self.make_temp_file(content = script, suffix = '.bat')
    cmd = f'{bat} foo bar'
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_shell(self):
    script = '''\
@echo off
echo %*
exit 0
'''
    bat = self.make_temp_file(content = script, suffix = '.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_success_flat_shell(self):
    script = '''\
@echo off
echo %*
exit 0
'''
    bat = self.make_temp_file(content = script, suffix = '.bat')
    cmd = f'"{bat}" foo bar'
    rv = execute.execute(cmd, shell = True, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure(self):
    script = '''\
@echo off
echo %*
exit 1
'''
    bat = self.make_temp_file(content = script, suffix = '.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_flat(self):
    script = '''\
@echo off
echo %*
exit 1
'''
    bat = self.make_temp_file(content = script, suffix = '.bat')
    cmd = f'"{bat}" foo bar'
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_shell(self):
    script = '''\
@echo off
echo %*
exit 1
'''
    bat = self.make_temp_file(content = script, suffix = '.bat')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_windows_batch_file_failure_flat_shell(self):
    script = '''\
@echo off
echo %*
exit 1
'''
    bat = self.make_temp_file(content = script, suffix = '.bat')
    cmd = f'"{bat}" foo bar'
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success(self):
    script = '''\
#!/bin/sh
echo "$@"
exit 0
'''
    bat = self.make_temp_file(content = script, perm = 0o0755, suffix = '.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_flat(self):
    script = '''\
#!/bin/sh
echo "$@"
exit 0
'''
    bat = self.make_temp_file(content = script, perm = 0o0755, suffix = '.sh')
    cmd = f'"{bat}" foo bar'
    rv = execute.execute(cmd, shell = False)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_shell(self):
    script = '''\
#!/bin/sh
echo "$@"
exit 0
'''
    bat = self.make_temp_file(content = script, perm = 0o0755, suffix = '.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_success_flat_shell(self):
    script = '''\
#!/bin/sh
echo "$@"
exit 0
'''
    bat = self.make_temp_file(content = script, perm = 0o0755, suffix = '.sh')
    cmd = f'"{bat}" foo bar'
    rv = execute.execute(cmd, shell = True, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure(self):
    script = '''\
#!/bin/sh
echo "$@"
exit 1
'''
    bat = self.make_temp_file(content = script, perm = 0o0755, suffix = '.sh')
    cmd = [ bat, 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_flat(self):
    script = '''\
#!/bin/sh
echo "$@"
exit 1
'''
    bat = self.make_temp_file(content = script, perm = 0o0755, suffix = '.sh')
    cmd = f'"{bat}" foo bar'
    rv = execute.execute(cmd, shell = False, raise_error = False)
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( 'foo bar', rv.stdout.strip() )
    
  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_shell(self):
    script = '''\
#!/bin/sh
echo "$@"
exit 1
'''
    bat = self.make_temp_file(content = script, perm = 0o0755, suffix = '.sh')
    cmd = [ f'"{bat}"', 'foo', 'bar' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_unix_shell_script_failure_flat_shell(self):
    script = '''\
#!/bin/sh
echo "$@"
exit 1
'''
    bat = self.make_temp_file(content = script, perm = 0o0755, suffix = '.sh')
    cmd = f'"{bat}" foo bar'
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  def test_python_script_success(self):
    content = '''\
import sys
print(f'success:{sys.argv[1]}')
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
print(f'failure:{sys.argv[1]}')
raise SystemExit(1)
'''
    script = self.make_temp_file(content = content, perm = 0o0755, suffix = '.py')
    cmd = [ script, 'foo' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 1, rv.exit_code )

  def test_python_script_uppercase_extension(self):
    content = '''\
import sys
print(f'success:{sys.argv[1]}')
raise SystemExit(0)
'''
    script = self.make_temp_file(content = content, perm = 0o0755, suffix = '.PY')
    cmd = [ script, 'foo' ]
    rv = execute.execute(cmd, shell = True, raise_error = False, quote = True)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'success:foo', rv.stdout.strip() )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_execute_stdout_stderr(self):
    script = '''\
#!/bin/sh
echo "this_is_stderr 1" >&2
echo "this_is_stdout 1" >&1
echo "this_is_stderr 2" >&2
echo "this_is_stdout 2" >&1
echo "this_is_stdout 3" >&1
echo "this_is_stdout 4" >&1
echo "this_is_stderr 3" >&2
echo "this_is_stderr 4" >&2
exit 0
'''
    bat = self.make_temp_file(content = script, perm = 0o0755)
    rv = execute.execute(bat, shell = False, raise_error = False)
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_fuzzy( r'''
this_is_stdout 1
this_is_stdout 2
this_is_stdout 3
this_is_stdout 4
''', rv.stdout )

    self.assert_string_equal_fuzzy( r'''
this_is_stderr 1
this_is_stderr 2
this_is_stderr 3
this_is_stderr 4
''', rv.stderr )
    
if __name__ == '__main__':
  unit_test.main()
