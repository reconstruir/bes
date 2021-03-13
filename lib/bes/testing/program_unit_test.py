#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import codecs, sys
import subprocess
import os.path as path
import platform

from .unit_test import unit_test

class program_unit_test(unit_test):

  @classmethod
  def _make_command(clazz, program, args):
    cmd = []
    if program.lower().endswith('.py'):
      cmd.append(sys.executable)
    cmd.append(program)
    cmd.extend(clazz._fix_args(args))
    return cmd

  @classmethod
  def _fix_args(clazz, args):
    '''
    Fix any arg that is a path to use unix style slashes
    Windows supports them and using them bypasses a bunch
    of quoting issues'
    '''
    is_windows = platform.system() == 'Windows'
    result = []
    for arg in args:
      if path.exists(arg):
        result.append(arg.replace('\\', '/'))
      else:
        result.append(arg)
    return result
  
  def run_program(self, program, args, cwd = None, env = None):
    rv = self.run_program_raw(program, args, cwd = cwd, env = env)
    if isinstance(rv.output, bytes):
      output = codecs.decode(rv.output, 'utf-8')
    else:
      output = rv.output
    if rv.exit_code != 0:
      print(rv.output)
    return self.exec_result(rv.exit_code, output)

  def run_program_raw(self, program, args, cwd = None, env = None):
    cmd = self._make_command(program, args)
    return self._exec(cmd, cwd, env)
  
  exec_result = namedtuple('exec_result', 'exit_code, output')
  @classmethod
  def _exec(clazz, cmd, cwd, env):
    process = subprocess.Popen(cmd, cwd = cwd, env = env, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = False)
    stdout, _ = process.communicate()
    exit_code = process.wait()
    return clazz.exec_result(exit_code, stdout.strip())

  def assert_rv_success(self, rv):
    if rv.exit_code != 0:
      sys.stdout.write(rv.stdout)
      sys.stdout.flush()
    self.assertEqual( 0, rv.exit_code )

  @classmethod
  def resolve_program(clazz, module_file, *parts):
    if not path.isabs(module_file):
      raise RuntimeError('module_file needs to be an absolute path to a python module file.')
    if not parts:
      raise RuntimeError('parts needs to be a non empty list of program parts for path.join()')
    return path.normpath(path.abspath(path.join(path.dirname(module_file), *parts)))
    
