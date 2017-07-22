#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path, pipes, re, shlex, subprocess, sys
from collections import namedtuple

class Shell(object):
  'Shell'

  Result = namedtuple('Result', [ 'stdout', 'stderr', 'exit_code' ])

  @classmethod
  def execute(clazz, command, raise_error = True, non_blocking = False, stderr_to_stdout = False,
              cwd = None, env = None, shell = False, input_data = None, universal_newlines = True):
    'Execute a command'

    def __make_args(command):
      if isinstance(command, list):
        return command
      else:
        return shlex.split(str(command))

    args = __make_args(command)

    stdout_pipe = subprocess.PIPE
    if not stderr_to_stdout:
      stderr_pipe = subprocess.PIPE
    else:
      stderr_pipe = subprocess.STDOUT

    if shell:
      args = ' '.join(args)
      # FIXME: quoting ?

    process = subprocess.Popen(args,
                               stdout = stdout_pipe,
                               stderr = stderr_pipe,
                               shell = shell,
                               cwd = cwd,
                               env = env,
                               universal_newlines = universal_newlines)

    # http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
    if non_blocking:
      # Poll process for new output until finished
      while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() != None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate(input_data)
    exit_code = process.wait()
    rv = clazz.Result(output[0], output[1], exit_code)
    if raise_error:
      if rv.exit_code != 0:
        raise RuntimeError(str(rv))
    return rv

  @classmethod
  def is_shell_script(clazz, filename):
    'Execute a command'
    with open(filename, 'r') as fp:
      magic = fp.read(2)
      return magic == '#!'

  @classmethod
  def listify_command(clazz, command):
    'Listify a command if needed'

    if isinstance(command, ( list )):
      return command
    else:
      return shlex.split(str(command))
