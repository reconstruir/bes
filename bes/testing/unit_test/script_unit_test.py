#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .unit_test import unit_test
from collections import namedtuple
import subprocess

class script_unit_test(unit_test):

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
  
  def make_command(self, *args):
    cmd = [ self._resolve_script() ] + list(args)
    return cmd

  def run_command(self, *args):
    cmd = self.make_command(*args)
    return self._exec(cmd)

  exec_result = namedtuple('exec_result', 'exit_code,stdout,stderr')
  @classmethod
  def _exec(clazz, cmd):
    process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
    stdout, stderr = process.communicate()
    exit_code = process.wait()
    return clazz.exec_result(exit_code, stdout.strip(), stderr.strip())
