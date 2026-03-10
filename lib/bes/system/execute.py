#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

import os
import re
import subprocess
import sys
import tempfile
import threading

from .check import check
from .command_line import command_line
from .compat import compat
from .env_override_options import env_override_options
from .env_override import env_override
from .execute_result import execute_result
from .host import host
from .log import logger
#from .os_env import os_env
from .python import python

_execute_progress_result = namedtuple('_execute_progress_result', 'result, events')

class execute(object):
  'Class to execute system commands with help for common usages.'

  _log = logger('execute')

  # Matches \r\n, \r, or \n as line separators (used by execute_with_progress).
  _LINE_SEP = re.compile(rb'\r\n|\r|\n')

  _output = namedtuple('_output', 'stdout, stderr')
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
              print_error = False,
              quote = False,
              check_python_script = True,
              output_encoding = None,
              output_function = None,
              env_options = None,
              log_error = False):
    'Execute a command'
    check.check_bytes(input_data, allow_none = True)
    check.check_bool(print_error)
    check.check_bool(quote)
    check.check_bool(check_python_script)
    check.check_string(output_encoding, allow_none = True)
    check.check_callable(output_function, allow_none = True)
    check.check_env_override_options(env_options, allow_none = True)
    check.check_bool(log_error)

    output_encoding = output_encoding or execute_result.DEFAULT_ENCODING
    
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

    if True:
      process = clazz.popen(args,
                            stderr_to_stdout = stderr_to_stdout,
                            cwd = cwd,
                            env = env,
                            shell = shell,
                            input_data = input_data,
                            print_error = print_error,
                            quote = quote,
                            check_python_script = check_python_script,
                            env_options = env_options)
      stdout_lines = []
      stderr_lines = []
      if non_blocking:
        stdout_lines, stderr_lines = clazz._poll_process(process,
                                                         output_encoding,
                                                         output_function,
                                                         stderr_pipe)

      clazz._log.log_d('execute: calling communicate with input_data={}'.format(input_data))
      output = process.communicate(input = input_data)

      exit_code = process.wait()
      clazz._log.log_d('execute: wait returned. exit_code={} output={}'.format(exit_code, output))
    
      if non_blocking:
        stdout = os.linesep.join(stdout_lines)
        stdout_bytes = stdout.encode(output_encoding)
        stderr = os.linesep.join(stderr_lines)
        stderr_bytes = stderr.encode(output_encoding)
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
          rv.raise_error(log_error = log_error, print_error = print_error)
      return rv

  @classmethod
  def popen(clazz,
            args = [],
            stderr_to_stdout = False,
            cwd = None,
            env = None,
            shell = False,
            input_data = None,
            print_error = False,
            quote = False,
            check_python_script = True,
            env_options = None,
            popen_fn = None):
    'Call subprocess.Popen (or popen_fn if provided, for testing injection).'
    check.check_bytes(input_data, allow_none = True)
    check.check_bool(print_error)
    check.check_bool(quote)
    check.check_bool(check_python_script)
    check.check_env_override_options(env_options, allow_none = True)
    check.check_callable(popen_fn, allow_none = True)

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

    _spawn = popen_fn or subprocess.Popen
    with env_override(options = env_options) as _:
      try:
        return _spawn(parsed_args,
                      stdout = stdout_pipe,
                      stderr = stderr_pipe,
                      stdin = stdin_pipe,
                      shell = shell,
                      cwd = cwd,
                      env = env)
      except OSError as ex:
        if print_error:
          message = 'failed: {} - {}'.format(str(parsed_args), str(ex))
          sys.stderr.write(message)
          sys.stderr.write('\n')
          sys.stderr.flush()
        raise
    
  @classmethod
  def _poll_process(clazz, process, output_encoding, output_function, stderr_pipe):
    # http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
    stdout_lines = []
    stderr_lines = []

    # Poll process for new output until finished
    while True:
      stdout_nextline = process.stdout.readline()
      stdout_decoded_nextline = stdout_nextline.decode(output_encoding, errors = 'ignore')
      clazz._log.log_d(f'execute: read stdout: {stdout_decoded_nextline}')
      stdout_is_empty = stdout_decoded_nextline == ''
      stderr_is_empty = True
      if stderr_pipe == subprocess.PIPE:
        stderr_nextline = process.stderr.readline()
        stderr_decoded_nextline = stderr_nextline.decode(output_encoding, errors = 'ignore')
        clazz._log.log_d(f'execute: read stderr: {stderr_decoded_nextline}')
        stderr_is_empty = stderr_decoded_nextline == ''

      if stdout_is_empty and stderr_is_empty and process.poll() != None:
        clazz._log.log_d('execute: non_blocking: process done')
        break

      stdout_lines.append(stdout_decoded_nextline)
      clazz._log.log_d(f'execute: non_blocking: stdout line: {stdout_decoded_nextline}')

      output_function_stdout = None
      if output_function:
        output_function_stdout = stdout_decoded_nextline
      else:
        sys.stdout.write(stdout_decoded_nextline)
        sys.stdout.flush()
        
      output_function_stderr = None
      if stderr_pipe == subprocess.PIPE:
        stderr_lines.append(stderr_decoded_nextline)
        clazz._log.log_d(f'execute: non_blocking: stderr line: {stderr_decoded_nextline}')
        if output_function:
          output_function_stderr = stderr_decoded_nextline
        else:
          sys.stderr.write(stderr_decoded_nextline)
          sys.stderr.flush()
      if output_function:
        output_function(clazz._output(output_function_stdout, output_function_stderr))
    return stdout_lines, stderr_lines
    
  @classmethod
  def execute_with_progress(clazz,
                            args,
                            line_parser,
                            progress_cb = None,
                            progress_source = 'both',
                            raise_error = False,
                            popen_fn = None,
                            **kwargs):
    '''Run a command and parse its output line-by-line for progress events.

    line_parser(stdout_line, stderr_line) -> event or None
      Called for each line from the stream(s) selected by progress_source.
      stdout_line is the line string when the line came from stdout, else None.
      stderr_line is the line string when the line came from stderr, else None.
      Return a non-None value to capture it as an event.

    progress_cb(event) -> None
      Called live (in the reader thread) for each non-None event.

    progress_source: 'stdout' | 'stderr' | 'both'
      Which stream triggers line_parser.  The other stream is captured silently
      and still included in the returned execute_result.  Default 'both'.

    raise_error: if True, raises RuntimeError on non-zero exit code.

    popen_fn: optional replacement for subprocess.Popen; used for test injection.

    Lines are split on \\r\\n, \\r, or \\n so tools that use \\r for in-place
    progress updates (e.g. whipper, cdparanoia) are handled correctly.

    Two threads read stdout and stderr concurrently, eliminating the deadlock
    that would occur if one pipe fills while the other is being read.

    The subprocess is always killed if an exception escapes from a callback.

    Returns _execute_progress_result(result, events).
    '''
    check.check_callable(line_parser)
    check.check_callable(progress_cb, allow_none = True)
    check.check_callable(popen_fn, allow_none = True)
    if 'non_blocking' in kwargs:
      raise ValueError('non_blocking is set internally by execute_with_progress')

    events = []
    _lock = threading.Lock()

    def _handle(stdout_line, stderr_line):
      with _lock:
        event = line_parser(stdout_line, stderr_line)
        if event is not None:
          events.append(event)
          if progress_cb:
            progress_cb(event)

    def _reader(pipe, raw_chunks, source_name):
      parse_buf = b''
      while True:
        data = pipe.read(4096)
        if not data:
          if parse_buf:
            line = parse_buf.decode('utf-8', errors = 'replace')
            if progress_source in (source_name, 'both'):
              stdout_arg = line if source_name == 'stdout' else None
              stderr_arg = line if source_name == 'stderr' else None
              _handle(stdout_arg, stderr_arg)
          break
        raw_chunks.append(data)
        parse_buf += data
        parts = clazz._LINE_SEP.split(parse_buf)
        for part in parts[:-1]:
          line = part.decode('utf-8', errors = 'replace')
          if progress_source in (source_name, 'both'):
            stdout_arg = line if source_name == 'stdout' else None
            stderr_arg = line if source_name == 'stderr' else None
            _handle(stdout_arg, stderr_arg)
        parse_buf = parts[-1]

    stderr_to_stdout = kwargs.pop('stderr_to_stdout', False)
    popen_kwargs = {k: v for k, v in kwargs.items()
                   if k in ('cwd', 'env', 'shell', 'quote',
                            'check_python_script', 'env_options', 'print_error')}
    popen_kwargs['stderr_to_stdout'] = stderr_to_stdout

    stdout_chunks = []
    stderr_chunks = []

    process = clazz.popen(args, popen_fn = popen_fn, **popen_kwargs)

    t_stdout = threading.Thread(
      target = _reader,
      args = (process.stdout, stdout_chunks, 'stdout'),
      daemon = True,
    )
    t_stderr = None
    if not stderr_to_stdout and process.stderr:
      t_stderr = threading.Thread(
        target = _reader,
        args = (process.stderr, stderr_chunks, 'stderr'),
        daemon = True,
      )

    try:
      t_stdout.start()
      if t_stderr:
        t_stderr.start()
      t_stdout.join()
      if t_stderr:
        t_stderr.join()
      exit_code = process.wait()
    except BaseException:
      try:
        process.kill()
        process.wait()
      except OSError:
        pass
      raise

    parsed_args = command_line.parse_args(args)
    result = execute_result(
      b''.join(stdout_chunks),
      b''.join(stderr_chunks),
      exit_code,
      parsed_args,
    )
    if raise_error and exit_code != 0:
      result.raise_error()
    return _execute_progress_result(result, events)

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

#  @classmethod
#  def execute_python_script(clazz, cmd):
#    fallback_python_path = path.normpath(path.join(path.dirname(__file__), '../../..'))
#    env = clazz.make_clean_env(keep_keys = [ 'PYTHONPATH' ])
#    env['PYTHONDONTWRITEBYTECODE'] = '1'
#    env['PYTHONPATH'] = env['PYTHONPATH'] + ':' + fallback_python_path
#    return execute.execute(cmd, env = env, raise_error = False, stderr_to_stdout = True)
      
