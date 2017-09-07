#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .unit_test import unit_test
from bes.common import Shell

class script_tester(unit_test):

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
    rv = Shell.execute(cmd, raise_error = False)
    if rv.exit_code != 0:
      print rv.stdout
      print rv.stderr
    return Shell.Result(rv.stdout.strip(), rv.stderr.strip(), rv.exit_code)
