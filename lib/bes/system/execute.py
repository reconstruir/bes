#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs, os, os.path as path, re, shlex, subprocess, sys, tempfile
from collections import namedtuple
from .compat import compat
from .host import host
from .python import python

class execute(object):
  'execute'

  Result = namedtuple('Result', [ 'stdout', 'stderr', 'exit_code' ])

  @classmethod
  def execute(clazz, command, raise_error = True, non_blocking = False, stderr_to_stdout = False,
              cwd = None, env = None, shell = False, input_data = None, universal_newlines = True,
              codec = None):
    'Execute a command'
    args = clazz.parse_args(command)
    stdout_pipe = subprocess.PIPE
    if not stderr_to_stdout:
      stderr_pipe = subprocess.PIPE
    else:
      stderr_pipe = subprocess.STDOUT

    # On windows run python scripts with python.exe
    if host.SYSTEM == host.WINDOWS:
      if path.exists(args[0]) and python.is_python_script(args[0]):
        from bes.python.py_exe import py_exe
        python_exe = py_exe.find_python_exe()
        args.insert(0, python_exe)
      
    if shell:
      args = ' '.join(args)
      # FIXME: quoting ?

    try:
      process = subprocess.Popen(args,
                                 stdout = stdout_pipe,
                                 stderr = stderr_pipe,
                                 shell = shell,
                                 cwd = cwd,
                                 env = env,
                                 universal_newlines = universal_newlines)
    except OSError as ex:
      message = 'failed: {} - {}'.format(str(args), str(ex))
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

    output = process.communicate(input_data)
    exit_code = process.wait()

    if stdout_lines:
      output = ( '\n'.join(stdout_lines), output[1] )
    
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
        print(str(ex))
        raise ex
    return rv

  @classmethod
  def parse_args(clazz, args):
    'Parse arguments to use for execute.'
    if host.SYSTEM == host.WINDOWS:
      return clazz._parse_args_windows(args)
    else:
      return clazz._parse_args_unix(args)
    
  @classmethod
  def _parse_args_unix(clazz, args):
    if compat.is_string(args):
      return shlex.split(args)
    elif isinstance(args, list):
      return args
    else:
      raise TypeError('args should be a string or list of strings instead of: {}'.format(args))
    
  @classmethod
  def _parse_args_windows(clazz, args):
    if compat.is_string(args):
      return clazz.win_CommandLineToArgvW(args)
    elif isinstance(args, list):
      return args
    else:
      raise TypeError('args should be a string or list of strings instead of: {}'.format(args))
    
  @classmethod
  def win_CommandLineToArgvW(clazz, cmd):
    import ctypes
    nargs = ctypes.c_int()
    ctypes.windll.shell32.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
    lpargs = ctypes.windll.shell32.CommandLineToArgvW(cmd, ctypes.byref(nargs))
    args = [lpargs[i] for i in range(nargs.value)]
    if ctypes.windll.kernel32.LocalFree(lpargs):
      raise AssertionError
    return args
  
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
