#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs, sys
import subprocess
import os.path as path
from .unit_test import unit_test
from collections import namedtuple

class script_unit_test(unit_test):

  @property
  def script(self):
    return self._resolve_script()
  
  @classmethod
  def _resolve_script(clazz):
    script = getattr(clazz, '__script__', None)
    if not script:
      raise RuntimeError('Missing __script__ attribute for %s' % (clazz))
    if not isinstance(script, tuple):
      raise TypeError('__script__ should be a 2 tuple instead of: %s - %s' % (str(script), type(script)))
    if len(script) != 2:
      raise TypeError('__script__ should be a 2 tuple instead of: %s - %s' % (str(script), type(script)))
    return clazz.file_path(script[0], script[1])
  
  def make_command(self, args):
    cmd = [ self._resolve_script() ] + list(args)
    return cmd

  def run_script(self, args, cwd = None, env = None):
    rv = self.run_script_raw(args, cwd = cwd, env = env)
    if isinstance(rv.output, bytes):
      output = codecs.decode(rv.output, 'utf-8')
    else:
      output = rv.output
    if rv.exit_code != 0:
      print(rv.output)
    return self.exec_result(rv.exit_code, output)

  def run_script_raw(self, args, cwd = None, env = None):
    cmd = self.make_command(args)
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
