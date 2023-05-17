#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import shlex
from .compat import compat
from .check import check
from .host import host

class command_line(object):
  'command_line'

  @classmethod
  def parse_args(clazz, args, quote = False, system = None):
    'Parse arguments to use for execute.'
    system = system or host.SYSTEM
    if system == host.WINDOWS:
      return clazz._parse_args_windows(args, quote = quote)
    elif system in ( host.MACOS, host.LINUX ):
      return clazz._parse_args_unix(args, quote = quote)
    else:
      host.raise_unsupported_system(system = system)
    
  @classmethod
  def _parse_args_unix(clazz, args, quote = False):
    assert args != None
    flat_args = None
    if compat.is_string(args):
      flat_args = args
    elif isinstance(args, ( list, tuple )):
      for i, arg in enumerate(args, start = 1):
        if arg == None:
          raise TypeError(f'arg {i} cannot be "None"')
        if not compat.is_string(arg):
          raise TypeError(f'arg should be a string instead of: "{arg}" - {type(arg)}')
      flat_args = ' '.join(args)
    else:
      raise TypeError('args should be a string or list of strings instead of: "{}" - {}'.format(args, type(args)))
    assert flat_args != None

    if quote:
      #assert False
      xflat_args = clazz.shell_quote(flat_args)
    return shlex.split(flat_args)
    
  @classmethod
  def _parse_args_windows(clazz, args, quote = False):
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
  def listify(clazz, command):
    'Listify a command if needed'
    if isinstance(command, ( list )):
      return command
    else:
      return shlex.split(str(command))


  @classmethod
  def shell_quote(clazz, s):
    'Quote spaces, quotes and other shell special chars'
    if compat.IS_PYTHON2:
      import pipes
      return pipes.quote(s)
    else:
      return shlex.quote(s)
    
  @classmethod
  def check_args_type(clazz, args):
    if check.is_string(args):
      return args
    if check.is_string_seq(args):
      return args
    raise TypeError(f'args should be a string, list or tuple: "{args}" - {type(args)}')
