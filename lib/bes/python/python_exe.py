#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
import os
import os.path as path
import sys
import subprocess

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.fs.file_path import file_path
from bes.fs.file_symlink import file_symlink
from bes.fs.file_util import file_util
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.os_env import os_env_var
from bes.system.which import which
from bes.version.software_version import software_version

from .python_error import python_error
from .python_version import python_version
from .python_source import python_source
from .python_script import python_script

class python_exe(object):
  'Class to deal with the python executable.'

  _log = logger('python_exe')
  
  @classmethod
  def full_version(clazz, exe):
    'Return the full version of a python executable'
    cmd = [ exe, '--version' ]
    rv = execute.execute(cmd, stderr_to_stdout = True)
    parts = string_util.split_by_white_space(rv.stdout, strip = True)
    if len(parts) != 2:
      raise python_error('not a valid python version for {}: "{}"'.format(exe, rv.stdout))
    if parts[0] != 'Python':
      raise python_error('not a valid python name for {}: "{}"'.format(exe, rv.stdout))
    return parts[1]

  @classmethod
  def version(clazz, exe):
    'Return the major.minor version of a python executable'
    full_version = clazz.full_version(exe)
    sv = software_version.parse_version(full_version)
    return '{}.{}'.format(sv.parts[0], sv.parts[1])

  @classmethod
  def major_version(clazz, exe):
    'Return the major version of a python executable'
    full_version = clazz.full_version(exe)
    sv = software_version.parse_version(full_version)
    return sv.parts[0]
  
  @classmethod
  def find_version(clazz, version, exclude_sources = None):
    'Return the python executable for major.minor version or None if not found'
    check.check_string(version)
    check.check_seq(exclude_sources, check.STRING_TYPES, allow_none = True)
    
    exclude_sources = set(exclude_sources or [])
    all_info = python_exe.find_all_exes_info()
    for next_exe, info in all_info.items():
      next_version = clazz.version(next_exe)
      if exclude_sources and info.source in exclude_sources:
        continue
      if next_version == version:
        return next_exe
    return None

  @classmethod
  def find_full_version(clazz, full_version):
    'Return the python executable for major.minor.revision full_version or None if not found'
    version = python_version.version(full_version)
    exe = clazz.find_version(version)
    if not exe:
      return None
    if clazz.full_version(exe) != full_version:
      return None
    return exe
  
  @classmethod
  def has_version(clazz, version):
    'Return True if python version major.minor is found'
    return clazz.find_version(version) != None

  @classmethod
  def has_full_version(clazz, full_version):
    'Return True if python version major.minor.revision is found'
    return clazz.find_full_version(full_version) != None

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

  _python_exe_info = namedtuple('_python_exe_info', 'exe, version, full_version, source, sys_executable, real_executable, exe_links, pip_exe')
  @classmethod
  def info(clazz, exe):
    'Return info for python executables'
    clazz.check_exe(exe)
    
    main_exe, exe_links = clazz._determine_main_exe_and_links(exe)
    from .python_installation_v2 import python_installation_v2
    piv = python_installation_v2(main_exe)
    sys_executable = python_script.sys_executable(main_exe)
    real_executable = file_symlink.resolve(sys_executable)
    source = python_source.exe_source(main_exe)
    version = clazz.version(main_exe)
    full_version = clazz.full_version(main_exe)
    return clazz._python_exe_info(main_exe,
                                  version,
                                  full_version,
                                  source,
                                  sys_executable,
                                  real_executable,
                                  exe_links,
                                  piv.pip_exe)

  @classmethod
  def _determine_main_exe_and_links(clazz, exe):
    'Return info for python executables'
    inode = file_util.inode_number(exe)
    exes = clazz._find_all_exes_in_PATH()
    inode_map = clazz._inode_map(exes)
    if not inode in inode_map:
      return exe, []
    links = inode_map[inode]
    main_exe = links.pop(0)
    return main_exe, links
  
  @classmethod
  def find_all_exes(clazz):
    'Return all the executables in PATH that match any patterns'
    all_exes = clazz._find_all_exes_in_PATH()
    inode_map = clazz._inode_map(all_exes)
    result = []
    for inode, exes in inode_map.items():
      main_exe = exes.pop(0)
      result.append(main_exe)
    return result
  
  @classmethod
  def find_all_exes_info(clazz):
    'Return info about all the executables in PATH that match any patterns'
    all_exes = clazz.find_all_exes()
    result = {}
    for next_exe in all_exes:
      result[next_exe] = clazz.info(next_exe)
    return result

  # Order in which versions are checked to return the default exe
  _DEFAULT_EXE_VERSION_LOOKUP_ORDER = [
    '3.7',
    '3.8',
    '3.9',
    '2.7',
  ]
  @classmethod
  def default_exe(clazz):
    'Return the default python executable'

    all_info = python_exe.find_all_exes_info()
    if not all_info:
      return None
    by_version = {}
    for _, next_info in all_info.items():
      by_version[next_info.version] = next_info
    for version in clazz._DEFAULT_EXE_VERSION_LOOKUP_ORDER:
      info = by_version.get(version, None)
      if info:
        return info.exe
    return by_version.items()[0].exe
  
  @classmethod
  def _find_all_exes_in_PATH(clazz):
    'Return all the executables in PATH that match any patterns'
    exe_patterns = python_source.possible_python_exe_patterns()
    extra_path = python_source.possible_python_bin_dirs()
    env_path = os_env_var('PATH').path + extra_path
    sanitized_env_path = clazz._sanitize_env_path(env_path)
    result = file_path.glob(sanitized_env_path, exe_patterns)
    clazz._log.log_d('      exe_patterns={}'.format(exe_patterns))
    clazz._log.log_d('          env_path={}'.format(env_path))
    clazz._log.log_d('        extra_path={}'.format(extra_path))
    clazz._log.log_d('sanitized_env_path={}'.format(sanitized_env_path))
    clazz._log.log_d('            result={}'.format(result))
    return result

  @classmethod
  def _sanitize_env_path(clazz, env_path):
    return [ entry for entry in env_path if not python_source.possible_python_dir_should_be_ignored(entry) ]
  
  @classmethod
  def _inode_map(clazz, exes):
    'Return an inode to list of executable map'
    result = {}
    for exe in exes:
      inode = file_util.inode_number(exe)
      if not inode in result:
        result[inode] = []
      result[inode].append(exe)
    sorted_result = {}
    for inode, links in result.items():
      sorted_result[inode] = sorted(result[inode], key = lambda exe: len(exe), reverse = True)
    return sorted_result

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
