#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

import re

from collections import namedtuple

from bes.common.check import check
from bes.system.execute import execute

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
    rv = execute.execute(cmd, stderr_to_stdout = True, print_failure = False)
    if rv.exit_code != 0:
      raise pip_error(str(ex))

    f = re.findall(clazz._PIP_VERSION_PATTERN, rv.stdout)
    if not f:
      raise pip_error('not a valid pip version for {}: "{}"'.format(pip_exe, rv.stdout))
    if len(f[0]) != 3:
      raise pip_error('not a valid pip version for {}: "{}"'.format(pip_exe, rv.stdout))
    version = f[0][0]
    where = f[0][1]
    python_version = f[0][2]
    return clazz._pip_version_info(version, where, python_version)

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
  
