#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import sys

from bes.common.check import check
from bes.common.string_util import string_util
from bes.fs.file_path import file_path
from bes.fs.file_symlink import file_symlink
from bes.system.execute import execute
from bes.system.host import host
from bes.system.which import which
from bes.version.software_version import software_version

from bes.unix.brew import brew

from .python_error import python_error
from .python_version import python_version

class python_exe(object):
  'Class to deal with the python executable.'

  @classmethod
  def full_version(clazz, exe):
    'Return the full version of a python executable'
    cmd = [ exe, '--version' ]
    rv = execute.execute(cmd, stderr_to_stdout = True)
    parts = string_util.split_by_white_space(rv.stdout, strip = True)
    if len(parts) != 2:
      raise python_error('not a valid python version for {}: "{}"'.format(exe, rv.stdout))
    if parts[0] != 'Python':
      raise python_error('not a valid python version for {}: "{}"'.format(exe, rv.stdout))
    return parts[1]

  @classmethod
  def version(clazz, exe):
    'Return the major.minor version of a python executable'
    full_version = clazz.full_version(exe)
    sv = software_version.parse_version(full_version)
    return '{}.{}'.format(sv.parts[0], sv.parts[1])

  @classmethod
  def find_python_version(clazz, version):
    'Return the python executable for major.minor version or None if not found'
    exe = 'python{}'.format(version)
    return which.which(exe, raise_error = False)

  @classmethod
  def find_python_full_version(clazz, full_version):
    'Return the python executable for major.minor.revision full_version or None if not found'
    version = python_version.full_version_to_version(full_version)
    exe = clazz.find_python_version(version)
    if not exe:
      return None
    if clazz.full_version(exe) != full_version:
      return None
    return exe
  
  @classmethod
  def has_python_version(clazz, version):
    'Return True if python version major.minor is found'
    return clazz.find_python_version(version) != None

  @classmethod
  def has_python_full_version(clazz, full_version):
    'Return True if python version major.minor.revision is found'
    return clazz.find_python_full_version(full_version) != None
  
  @classmethod
  def macos_is_from_brew(clazz, exe):
    'Return True if exe is from brew'
    host.check_is_macos()

    if not brew.has_brew():
      return False
    
    if not path.isabs(exe):
      raise python_error('exe should be an absolute path: "{}"'.format(exe))
    
    actual_exe = file_symlink.resolve(exe)
    return 'cellar' in actual_exe.lower()

  @classmethod
  def macos_is_builtin(clazz, exe):
    'Return True if the given python executable is the sytem python that comes with macos'
    host.check_is_macos()

    if not path.isabs(exe):
      raise python_error('exe should be an absolute path: "{}"'.format(exe))
    return exe.lower().startswith('/usr/bin/python')

  @classmethod
  def check_exe(clazz, python_exe, check_abs = True):
    'Check that python_exe appears to be a valid python exe and raise an error if not'
    check.check_string(python_exe)
    check.check_bool(check_abs)

    if check_abs and not path.isabs(python_exe):
      raise python_error('not an absolute path: "{}"'.format(python_exe))
  
    if not file_path.is_executable(python_exe):
      raise python_error('not a valid executable: "{}"'.format(python_exe))

    return clazz.full_version(python_exe)
  
  @classmethod
  def exe_for_sys_version(clazz, absolute = True):
    'Return the python executable binary for sys.version (python2.7, python3.7, etc)'
    check.check_bool(absolute)

    exe = 'python{major}.{minor}'.format(major = sys.version_info.major,
                                         minor = sys.version_info.minor)
    if absolute:
      return which.which(exe)
    else:
      return exe
