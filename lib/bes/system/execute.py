#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re, subprocess, sys, tempfile

from .check import check
from .command_line import command_line
from .compat import compat
from .execute_result import execute_result
from .host import host
from .log import logger
from .python import python

class execute(object):
  'Class to execute system commands with help for common usages.'

  _log = logger('execute')
  
  @classmethod
  def execute(clazz,
              args,
              raise_error = True,
              non_blocking = False,
              stderr_to_stdout = False,
              cwd = None,
              env = None,
              shell = False,
              input_data = None,
              print_failure = True,
              quote = False,
              check_python_script = True):
    'Execute a command'
    check.check_bytes(input_data, allow_none = True)
    check.check_bool(print_failure)
    check.check_bool(quote)
    check.check_bool(check_python_script)
    
    clazz._log.log_method_d()
    
    parsed_args = command_line.parse_args(args, quote = quote)
    stdout_pipe = subprocess.PIPE
    if not stderr_to_stdout:
      stderr_pipe = subprocess.PIPE
    else:
      stderr_pipe = subprocess.STDOUT
    if input_data != None:
      stdin_pipe = subprocess.PIPE
    else:
      stdin_pipe = None

    # If the first argument is a python script, then run it with python always
    if check_python_script:
      if path.exists(parsed_args[0]) and python.is_python_script(parsed_args[0]):
        python_exe = python.find_python_exe()
        if ' ' in python_exe:
          python_exe = '"{}"'.format(python_exe)
        parsed_args.insert(0, python_exe)

    if shell:
      parsed_args = ' '.join(parsed_args)
      # FIXME: quoting ?
      
    clazz._log.log_d('parsed_args={}'.format(parsed_args))
    try:
      process = subprocess.Popen(parsed_args,
                                 stdout = stdout_pipe,
                                 stderr = stderr_pipe,
                                 stdin = stdin_pipe,
                                 shell = shell,
                                 cwd = cwd,
                                 env = env)
    except OSError as ex:
      if print_failure:
        message = 'failed: {} - {}'.format(str(parsed_args), str(ex))
        sys.stderr.write(message)
        sys.stderr.write('\n')
        sys.stderr.flush()
      raise

    # http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
    stdout_lines = []
    if non_blocking:
      # Poll process for new output until finished
      while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() != None:
            break
        stdout_lines.append(nextline)
        sys.stdout.write(nextline)
        sys.stdout.flush()

    clazz._log.log_d('execute: calling communicate with input_data={}'.format(input_data))
    output = process.communicate(input = input_data)
    exit_code = process.wait()
    clazz._log.log_d('execute: wait returned. exit_code={} output={}'.format(exit_code, output))
    
    if stdout_lines:
      output = ( '\n'.join(stdout_lines), output[1] )
    
#    if codec:
#      stdout = codecs.decode(output[0], codec, 'ignore')
#      if output[1]:
#        stderr = codecs.decode(output[1], codec, 'ignore')
#      else:
#        stderr = None
    else:
      stdout_bytes = output[0]
      stderr_bytes = output[1] or b''
    if stdout_bytes:
      assert check.is_bytes(stdout_bytes)
    if stderr_bytes:
      assert check.is_bytes(stderr_bytes)
    rv = execute_result(stdout_bytes, stderr_bytes, exit_code, parsed_args)
    if raise_error:
      if rv.exit_code != 0:
        rv.raise_error(log_error = True, print_error = True)
    return rv

  @classmethod
  def parse_args(clazz, args, quote = False):
    'Parse arguments to use for execute.'
    return command_line.parse_args(args, quote = quote)
    
  @classmethod
  def is_shell_script(clazz, filename):
    'Execute a command'
    with open(filename, 'r') as fp:
      magic = fp.read(2)
      return magic == '#!'

  @classmethod
  def listify_command(clazz, command):
    'Listify a command if needed'
    return command_line.listify(command)

  @classmethod
  def execute_from_string(clazz,
                          content,
                          raise_error = True,
                          non_blocking = False,
                          stderr_to_stdout = False,
                          cwd = None,
                          env = None,
                          shell = False,
                          input_data = None):
    assert string_util.is_string(content)
    tmp = tempfile.mktemp()
    with open(tmp, 'w') as fout:
      fout.write(content)
      os.chmod(tmp, 0o755)
    try:
      return clazz.execute(tmp, raise_error = raise_error, non_blocking = non_blocking,
                           stderr_to_stdout = stderr_to_stdout, cwd = cwd,
                           env = env, shell = shell, input_data = input_data)
    except:
      raise
    finally:
      os.remove(tmp)
