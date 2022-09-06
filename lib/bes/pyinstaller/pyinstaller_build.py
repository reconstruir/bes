#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import copy
import os
from os import path
import sys

from ..common.string_util import string_util
from ..fs.file_util import file_util
from ..fs.filename_util import filename_util
from ..fs.temp_file import temp_file
from ..system.check import check
from ..system.command_line import command_line
from ..system.env_override_options import env_override_options
from ..system.host import host
from ..system.log import logger

from .pyinstaller_error import pyinstaller_error
from .pyinstaller_exe import pyinstaller_exe
from .pyinstaller_log_level import pyinstaller_log_level
from .pyinstaller_options import pyinstaller_options

class pyinstaller_build(object):
  'Class to deal with pyinstaller build.'
  
  log = logger('pyinstaller')

  _build_result = namedtuple('_build_result', 'output_exe')
  @classmethod
  def build(clazz, script_filename, options = None):
    check.check_string(script_filename)
    check.check_pyinstaller_options(options, allow_none = True)

    options = options or pyinstaller_options()
    
    if not path.isfile(script_filename):
      raise pyinstaller_error('script filename not found: "{}"'.format(script_filename))
        
    excludes = options.excludes or []
    hidden_imports = options.hidden_imports or []

    basic_args = [ '--onefile' ]
    if options.osx_bundle_identifier:
      basic_args.extend([ '--osx-bundle-identifier', options.osx_bundle_identifier ])
    if options.windowed:
      basic_args.append('--windowed')
    log_args = [ '--log-level', options.log_level.name ]
    excludes_args = clazz._make_arg_pair_list('--exclude', excludes)
    hidden_imports_args = clazz._make_arg_pair_list('--hidden-import', hidden_imports)

#    if sys.version_info.minor >= 10:
#      python_10_args = [ '--exclude-module', '_bootlocale' ]
#    else:
#      python_10_args = []
    python_10_args = []
    
    args = basic_args + log_args + excludes_args + hidden_imports_args + python_10_args + [ script_filename ]

    build_dir = path.abspath(options.build_dir)
    output_exe = path.join(build_dir, 'dist', clazz._binary_filename(script_filename))

    if options.clean:
      file_util.remove(build_dir)

    pyinstaller_exe.call_pyinstaller(args,
                                     build_dir = build_dir,
                                     env_options = options.env_options)
    return clazz._build_result(output_exe)

  @classmethod
  def _make_arg_pair_list(clazz, flag, items):
    pairs = [ '{} {}'.format(flag, item) for item in items ]
    flat = ' '.join(pairs)
    return string_util.split_by_white_space(flat)

  @classmethod                          
  def _binary_filename(clazz, script_filename):
    basename = path.basename(filename_util.without_extension(script_filename))
    if host.is_windows():
      return basename + '.exe'
    return basename
