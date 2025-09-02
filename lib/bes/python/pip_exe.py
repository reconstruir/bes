#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
from os import path
import subprocess

import re

from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.fs.file_mime import file_mime
from bes.fs.filename_util import filename_util
from bes.system.execute import execute
from bes.system.host import host
from bes.system.log import logger

from ..files.bf_glob import bf_glob

from .python_error import python_error
from .python_exe import python_exe as bes_python_exe
from .python_pip_exe import python_pip_exe as python_pip_exe
from .python_version import python_version as bes_python_version

from .pip_error import pip_error

class pip_exe(object):
  'Class to deal with the pip executable.'

  _log = logger('pip')
  
  @classmethod
  def version_info(clazz, pip_exe):
    'Return the version info of a pip executable'
    check.check_string(pip_exe)

    filename_info = clazz.filename_info(pip_exe)
    pythonpath = [ filename_info.libdir ] if filename_info.libdir else None
    try:
      return python_pip_exe.version_info(pip_exe, pythonpath = pythonpath)
    except python_error as ex:
      raise pip_error(ex.message, status_code = ex.status_code)

  _pip_filename_info = namedtuple('_pip_filename_info', 'version, libdir')
  @classmethod
  def filename_info(clazz, pip_exe):
    'Return info about the pip exe filename'
    check.check_string(pip_exe)

    if host.is_windows():
      pip_exe_lower = pip_exe.lower()
      ext = filename_util.extension(pip_exe_lower)
      if ext in ( 'cmd', 'exe', 'bat', 'ps1' ):
        basename = filename_util.without_extension(path.basename(pip_exe_lower))
      else:
        basename = path.basename(pip_exe_lower)
    else:
      basename = path.basename(pip_exe)
    if not basename.startswith('pip'):
      return clazz._pip_filename_info(None, None)
    version = string_util.remove_head(basename, 'pip')
    version_parts = [ p for p in version.split('.') if p ]
    num_version_parts = len(version_parts)
    if num_version_parts not in ( 1, 2 ):
      version = None
    libdir = clazz._pip_exe_determine_libdir(pip_exe, version)
    return clazz._pip_filename_info(version, libdir)

  @classmethod
  def _pip_exe_determine_libdir(clazz, pip_exe, version):
    'Determine the PYTHONPATH needed to run a pip exe'
    assert pip_exe

    if clazz.is_binary(pip_exe):
      return None
    
    root_dir = path.dirname(pip_exe)
    lib_dir = path.normpath(path.join(path.join(root_dir, path.pardir), 'lib'))
    possible_python_libdirs = bf_glob.glob(lib_dir, 'python*')
    num_possible_python_libdirs = len(possible_python_libdirs)
    if num_possible_python_libdirs == 1:
      python_libdir = possible_python_libdirs[0]
    else:
      python_libdir = None
    if not python_libdir:
      return None
    if not python_libdir:
      return None
    possible_site_packages_dir = path.join(python_libdir, 'site-packages')
    if path.isdir(possible_site_packages_dir):
      return possible_site_packages_dir
    return None
  
  @classmethod
  def version(clazz, pip_exe):
    'Return the version of a pip executable'
    check.check_string(pip_exe)

    return clazz.version_info(pip_exe).version

  @classmethod
  def is_binary(clazz, pip_exe):
    'Return True if the pip_exe is an executable instead of a python script'
    check.check_string(pip_exe)

    return file_mime.is_binary(pip_exe)
  
  @classmethod
  def find_exe_for_python(clazz, python_exe):
    'Find pip executable for a specific python exe'
    bes_python_exe.check_exe(python_exe)

    if host.is_windows():
      result = clazz._find_exe_for_python_windows(python_exe)
    elif host.is_unix():
      result = clazz._find_exe_for_python_unix(python_exe)
    else:
      host.raise_unsupported_system()
    return result

  @classmethod
  def _find_exe_for_python_windows(clazz, python_exe):
    version = bes_python_exe.version(python_exe)
    major_version = bes_python_version.major_version(version)
    clazz._log.log_d('_find_exe_for_python_windows: python_exe={} version={} major_version={}'.format(python_exe,
                                                                                                      version,
                                                                                                      major_version))
    dirname = path.dirname(python_exe)
    possible_pips = [
      path.join(dirname, 'pip{}.exe'.format(version)),
      path.join(dirname, 'pip{}.exe'.format(major_version)),
      path.join(dirname, 'Scripts', 'pip{}.exe'.format(version)),
      path.join(dirname, 'Scripts', 'pip{}.exe'.format(major_version)),
    ]
    for p in possible_pips:
      if path.exists(p):
        return p
    return None
  
  @classmethod
  def _find_exe_for_python_unix(clazz, python_exe):
    version = bes_python_exe.version(python_exe)
    major_version = bes_python_version.major_version(version)
    clazz._log.log_d('_find_exe_for_python_unix: python_exe={} version={} major_version={}'.format(python_exe,
                                                                                                  version,
                                                                                                  major_version))
    dirname = path.dirname(python_exe)
    possible_pips = [
      path.join(dirname, 'pip{}'.format(version)),
      path.join(dirname, 'pip{}'.format(major_version)),
    ]
    for p in possible_pips:
      if path.exists(p):
        return p
    return None
