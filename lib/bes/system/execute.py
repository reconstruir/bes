#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs, os, os.path as path, pipes, re, shlex, subprocess, sys, tempfile
from collections import namedtuple

class execute(object):
  'execute'

  Result = namedtuple('Result', [ 'stdout', 'stderr', 'exit_code' ])

  @classmethod
  def execute(clazz, command, raise_error = True, non_blocking = False, stderr_to_stdout = False,
              cwd = None, env = None, shell = False, input_data = None, universal_newlines = True,
              codec = None):
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

    if codec:
      stdout = codecs.decode(output[0], codec)
      stderr = codecs.decode(output[1], codec)
    else:
      stdout = output[0]
      stderr = output[1]
    
    rv = clazz.Result(stdout, stderr, exit_code)
    if raise_error:
      if rv.exit_code != 0:
        ex = RuntimeError(rv.stdout)
        setattr(ex, 'execute_result', rv)
        print(rv.stdout)
        print(rv.stderr)
        raise ex
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

  @classmethod
  def execute_from_string(clazz, content, raise_error = True, non_blocking = False, stderr_to_stdout = False,
                          cwd = None, env = None, shell = False, input_data = None, universal_newlines = True,
                          codec = None):
    assert string_util.is_string(content)
    tmp = tempfile.mktemp()
    with open(tmp, 'w') as fout:
      fout.write(content)
      os.chmod(tmp, 0o755)
    try:
      return clazz.execute(tmp, raise_error = raise_error, non_blocking = non_blocking,
                           stderr_to_stdout = stderr_to_stdout, cwd = cwd,
                           env = env, shell = shell, input_data = input_data,
                           universal_newlines = universal_newlines, codec = codec)
    except:
      raise
    finally:
      os.remove(tmp)
