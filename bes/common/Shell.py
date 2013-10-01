#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ObjectUtil import ObjectUtil
import shlex, subprocess

class Shell(object):
  'Shell'

  @classmethod
  def execute(clazz, command):
    'Execute a command'

    def __make_args(command):
      if isinstance(command, list):
        return command
      else:
        return shlex.split(str(command))

    args = __make_args(command)
    process = subprocess.Popen(args,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE)

    output = process.communicate()
    exit_code = process.wait()
    return ObjectUtil.make('ExecResult', { 'stdout': output[0], 'stderr': output[1], 'exit_code': exit_code })
