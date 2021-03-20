#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import subprocess

import re

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.system.execute import execute
from bes.system.env_override import env_override
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util

from bes.python.python_exe import python_exe
from bes.python.python_version import python_version

from .pip_error import pip_error

class pip_exe(object):
  'Class to deal with the python executable.'

  _PIP_VERSION_PATTERN = r'^pip\s+([\d\.]+)\s+from\s+(.+)\s+\(python\s+(\d+\.\d+)\)$'
  
  _pip_version_info = namedtuple('_pip_version_info', 'version, where, python_version')
  @classmethod
  def version_info(clazz, pip_exe):
    'Return the version info of a pip executable'
    check.check_string(pip_exe)

    cmd = [ pip_exe, '--version' ]

    filename_info = clazz.filename_info(pip_exe)
    libdir = filename_info.libdir or ''
    with env_override(env = { 'PYTHONPATH': libdir }) as env:
      try:
        output = subprocess.check_output(cmd, stderr = subprocess.STDOUT)
      except subprocess.CalledProcessError as ex:
        msg = 'Failed to run: "{}" - {}'.format(' '.join(cmd), ex.output)
        raise pip_error(msg, status_code = ex.returncode)

    f = re.findall(clazz._PIP_VERSION_PATTERN, output)
    if not f:
      raise pip_error('not a valid pip version for {}: "{}"'.format(pip_exe, output))
    if len(f[0]) != 3:
      raise pip_error('not a valid pip version for {}: "{}"'.format(pip_exe, output))
    version = f[0][0]
    where = f[0][1]
    python_version = f[0][2]
    return clazz._pip_version_info(version, where, python_version)

  _pip_filename_info = namedtuple('_pip_filename_info', 'version, libdir')
  @classmethod
  def filename_info(clazz, pip_exe):
    'Return info about the pip exe filename'
    check.check_string(pip_exe)

    basename = path.basename(pip_exe).lower()
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

    if file_mime.is_binary(pip_exe):
      return None
    
    root_dir = path.dirname(pip_exe)
    lib_dir = path.normpath(path.join(path.join(root_dir, path.pardir), 'lib'))
    possible_python_libdirs = file_path.glob(lib_dir, 'python*')
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
  def pip_exe(clazz, py_exe):
    'Return the pip executable for the given python'
    check.check_string(py_exe)

    python_exe.check_exe(py_exe)
    py_version = python_exe.version(py_exe)

    exe = clazz._pip_exe_for_python_exe(py_exe)
    if not exe:
      raise pip_error('No pip found for python exe: "{}"'.format(py_exe))
    return exe

  @classmethod
  def pip_exe_is_valid(clazz, pip_exe):
    'Return True if the given pip exeecutable is valid'
    check.check_string(pip_exe)

    try:
      clazz.version_info(pip_exe)
      return True
    except Exception as ex:
      pass
    return False

  @classmethod
  def _pip_exe_for_python_exe(clazz, py_exe):
    'Return the pip executable for the given python'
    check.check_string(py_exe)

    python_exe.check_exe(py_exe)
    py_version = python_exe.version(py_exe)
    python_bin_dir = path.dirname(py_exe)
    possible_basenames = [
      'pip{}'.format(py_version),
      'pip{}'.format(python_version.any_version_to_major_version(py_version)),
    ]
    for possible_basename in possible_basenames:
      possible_pip_exe = path.join(python_bin_dir, possible_basename)
      if path.exists(possible_pip_exe):
        return possible_pip_exe
    return None
  
