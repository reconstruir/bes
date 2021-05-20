#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import os, re
from os import path

from bes.common.check import check
from bes.fs.temp_file import temp_file
from bes.system.command_line import command_line
from bes.system.log import logger

from .pyinstaller_error import pyinstaller_error
from .pyinstaller_exe import pyinstaller_exe

class pyinstaller_build(object):
  'Class to deal with pyinstaller build.'
  
  log = logger('pyinstaller')

  VALID_LOG_LEVELS = [ 'DEBUG', 'INFO' ]
  
  @classmethod
  def build(clazz, script_filename,
            python_path = None,
            log_level = None,
            excludes = None,
            hidden_imports = None,
            verbose = False,
            cwd = None,
            replace_env = None,
            exe = None):
    check.check_string(script_filename)
    check.check_string_seq(python_path, allow_none = True)
    check.check_string(log_level, allow_none = True)
    check.check_string_seq(excludes, allow_none = True)
    check.check_string_seq(hidden_imports, allow_none = True)
    check.check_string(cwd, allow_none = True)
    check.check_bool(verbose)
    check.check_string(exe, allow_none = True)

    if not path.isfile(script_filename):
      raise pyinstaller_error('script filename not found: "{}"'.format(script_filename))

    log_level = log_level or 'INFO'
    if log_level not in clazz.VALID_LOG_LEVELS:
      raise pyinstaller_error('Invalid log level: "{}" - Should be one of '.format(' '.join(clazz.VALID_LOG_LEVELS)))
      
    python_path = python_path or []
    for p in python_path:
      if not path.isdir(p):
        raise pyinstaller_error('PYTHONPATH dir not found: "{}"'.format(p))
        
    excludes = excludes or []
    hidden_imports = hidden_imports or []

    basic_args = [ '--onefile' ]
    log_args = [ '--log', log_level ]
    excludes_args = clazz._make_arg_pair_list('--exclude', excludes)
    hidden_imports_args = clazz._make_arg_pair_list('--hidden-import', hidden_imports)

    args = basic_args + log_args + excludes_args + hidden_imports_args + [ script_filename ]

    replace_env = copy.deepcopy(replace_env or {})
    if python_path:
      replace_env['PYTHONPATH'] = os.pathsep.join(python_path)
    
    pyinstaller_exe.call_pyinstaller(args,
                                     replace_env = replace_env,
                                     non_blocking = verbose,
                                     cwd = cwd,
                                     exe = exe)

  @classmethod
  def _make_arg_pair_list(clazz, flag, items):
    pairs = [ '{} {}'.format(flag, item) for item in items ]
    flat = ' '.join(pairs)
    return command_line.parse_args(flat)
