#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs
import os
import os.path as path
import sys

from collections import namedtuple
from collections import OrderedDict

from ..system.check import check
from bes.common.string_util import string_util
from bes.debug.debug_timer import debug_timer
from bes.fs.file_path import file_path
from bes.fs.file_symlink import file_symlink
from bes.fs.file_util import file_util
from bes.system.execute import execute
from bes.system.log import logger
from bes.system.os_env import os_env_var
from bes.system.which import which
from bes.version.semantic_version import semantic_version
from bes.debug.debug_timer import timed_function

from ..files.bf_glob import bf_glob

from .python_debug import python_debug
from .python_error import python_error
from .python_exe_info import python_exe_info
from .python_script import python_script
from .python_source import python_source
from .python_version import python_version

class python_exe(object):
  'Class to deal with the python executable.'

  _log = logger('python_exe')

  @classmethod
  def full_version(clazz, exe):
    'Return the full version of a python executable'
    cmd = [ exe, '--version' ]
    rv = execute.execute(cmd)
    stdout = rv.stdout.strip()
    stderr = rv.stderr.strip()
    output = stdout or stderr
    parts = string_util.split_by_white_space(output, strip = True)
    if len(parts) != 2:
      raise python_error(f'not a valid python version for {exe}: "{output}"')
    if parts[0] != 'Python':
      raise python_error(f'not a valid python name for {exe}: "{output}"')
    return python_version(parts[1])

  @classmethod
  def version(clazz, exe):
    'Return the major.minor version of a python executable'
    return clazz.full_version(exe).version

  @classmethod
  def semantic_version(clazz, exe):
    'Return the semantic major.minor version of a python executable'
    return semantic_version(str(clazz.version(exe)))
  
  @classmethod
  def major_version(clazz, exe):
    'Return the major version of a python executable'
    return clazz.full_version(exe).major_version
  
  @classmethod
  def find_version_info(clazz, version, exclude_sources = None, sanitize_path = True):
    'Return the python executable for major.minor version or None if not found'
    version = python_version.check_version(version)
    check.check_seq(exclude_sources, check.STRING_TYPES, allow_none = True)
    
    all_info = clazz.find_all_exes_info(exclude_sources = exclude_sources,
                                        sanitize_path = sanitize_path)
    for next_exe, info in all_info.items():
      if info.version == version:
        return info
    return None

  @classmethod
  def find_version(clazz, version, exclude_sources = None, sanitize_path = True):
    'Return the python executable for major.minor version or None if not found'
    info = clazz.find_version_info(version,
                                   exclude_sources = exclude_sources,
                                   sanitize_path = sanitize_path)
    if not info:
      return None
    return info.exe
  
  @classmethod
  def find_full_version_info(clazz, full_version, exclude_sources = None, sanitize_path = True):
    'Return the python executable for major.minor version or None if not found'
    version = python_version.check_version(full_version)
    check.check_seq(exclude_sources, check.STRING_TYPES, allow_none = True)
    
    all_info = clazz.find_all_exes_info(exclude_sources = exclude_sources,
                                             sanitize_path = sanitize_path)
    for next_exe, info in all_info.items():
      if info.full_version == full_version:
        return info
    return None

  @classmethod
  def find_full_version(clazz, full_version, exclude_sources = None, sanitize_path = True):
    'Return the python executable for major.minor version or None if not found'
    info = clazz.find_full_version_info(full_version,
                                        exclude_sources = exclude_sources,
                                        sanitize_path = sanitize_path)
    if not info:
      return None
    return info.exe
  
  @classmethod
  def has_version(clazz, version, sanitize_path = True):
    'Return True if python version major.minor is found'
    return clazz.find_version(version, sanitize_path = sanitize_path) != None

  @classmethod
  def has_full_version(clazz, full_version, sanitize_path = True):
    'Return True if python version major.minor.revision is found'
    return clazz.find_full_version(full_version, sanitize_path = sanitize_path) != None

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

  _info_cache = {}
  @classmethod
  #@timed_function(python_debug.timer)
  def info(clazz, exe):
    'Return info for python executables'
    clazz.check_exe(exe)

    if not exe in clazz._info_cache:
      clazz._info_cache[exe] = clazz._make_info(exe)
    assert exe in clazz._info_cache
    return clazz._info_cache[exe]

  @classmethod
  def _make_info(clazz, exe):
    main_exe, exe_links = clazz._determine_main_exe_and_links(exe)
    from .python_installation import python_installation
    piv = python_installation(main_exe)
    sys_executable = python_script.sys_executable(main_exe)
    real_executable = file_symlink.resolve(sys_executable)
    source = python_source.exe_source(main_exe)
    version = clazz.version(main_exe)
    full_version = clazz.full_version(main_exe)
    return python_exe_info(main_exe,
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
    exes = clazz._find_all_exes()
    inode_map = clazz._inode_map(exes)
    if not inode in inode_map:
      return exe, []
    links = inode_map[inode]
    main_exe = links.pop(0)
    return main_exe, links
  
  @classmethod
  def find_all_exes(clazz, sanitize_path = True):
    'Return all the executables in PATH that match any patterns'
    all_exes = clazz._find_all_exes(sanitize_path = sanitize_path)
    inode_map = clazz._inode_map(all_exes)
    result = []
    for inode, exes in inode_map.items():
      main_exe = exes.pop(0)
      result.append(main_exe)
    return result
  
  @classmethod
  def find_all_exes_info(clazz, exclude_sources = None, sanitize_path = True, key_by_version = False):
    'Return an ordered dict of info about all the executables in PATH that match any patterns'
    check.check_seq(exclude_sources, check.STRING_TYPES, allow_none = True)

    exclude_sources = set(exclude_sources or [])
    all_exes = clazz.find_all_exes(sanitize_path = sanitize_path)
    result = OrderedDict()
    for next_exe in all_exes:
      info = clazz.info(next_exe)
  @classmethod
  def _determine_main_exe_and_links(clazz, exe):
    'Return info for python executables'
    inode = file_util.inode_number(exe)
    exes = clazz._find_all_exes()
    inode_map = clazz._inode_map(exes)
    if not inode in inode_map:
      return exe, []
    links = inode_map[inode]
    main_exe = links.pop(0)
    return main_exe, links
  
  @classmethod
  def find_all_exes(clazz, sanitize_path = True):
    'Return all the executables in PATH that match any patterns'
    all_exes = clazz._find_all_exes(sanitize_path = sanitize_path)
    inode_map = clazz._inode_map(all_exes)
    result = []
    for inode, exes in inode_map.items():
      main_exe = exes.pop(0)
      result.append(main_exe)
    return result
  
  @classmethod
  def find_all_exes_info(clazz, exclude_sources = None, sanitize_path = True, key_by_version = False):
    'Return an ordered dict of info about all the executables in PATH that match any patterns'
    check.check_seq(exclude_sources, check.STRING_TYPES, allow_none = True)

    exclude_sources = set(exclude_sources or [])
    all_exes = clazz.find_all_exes(sanitize_path = sanitize_path)
    result = OrderedDict()
    for next_exe in all_exes:
      info = clazz.info(next_exe)
      if info.source not in exclude_sources:
        if key_by_version:
          key = str(info.version)
        else:
          key = next_exe
        result[key] = info
    return result

  @classmethod
  def available_versions(clazz):
    'Return a set of all available python versions'
    infos = clazz.find_all_exes_info()
    return set([ str(info.version) for _, info in infos.items() ])
  
  @classmethod
  def default_exe(clazz):
    'Return the default python executable'
    all_info = clazz.find_all_exes_info()
    if not all_info:
      return None
    items = sorted([ item for _, item in all_info.items() ], key = lambda item: item.version, reverse = True)
    return items[0].exe

  @classmethod
  def default_exe_version(clazz):
    'Return the version for the default python executable'
    exe = clazz.default_exe()
    if not exe:
      return None
    return clazz.version(exe).version

  @classmethod
  def _exe_version_is_good(clazz, exe):
    sv = clazz.semantic_version(exe)
    #print(f'checking {exe} {sv}')
    return sv >= '3.8' and sv <= '3.13'
  
  _all_exes_cache = {}
  @classmethod
  #@timed_function(python_debug.timer)
  def _find_all_exes(clazz, sanitize_path = True):
    'Return all the executables in PATH and other platform specific places'
    if not sanitize_path in clazz._all_exes_cache:
      exe_patterns = python_source.possible_python_exe_patterns()
      extra_path = python_source.possible_python_bin_dirs()
      env_path = os_env_var('PATH').path + extra_path
      if sanitize_path:
        sanitized_env_path = clazz._sanitize_env_path(env_path)
      else:
        sanitized_env_path = env_path
      result = bf_glob.glob(sanitized_env_path, exe_patterns)
      result = [ f for f in result if not file_symlink.is_broken(f) ]

      seen = set()
      c = []
      for exe in result:
        inode = file_util.inode_number(exe)
        if not inode in seen:
          seen.add(inode)
          if clazz._exe_version_is_good(exe):
            c.append(exe)
      result = c
      clazz._log.log_d('      exe_patterns={}'.format(exe_patterns))
      clazz._log.log_d('          env_path={}'.format(env_path))
      clazz._log.log_d('        extra_path={}'.format(extra_path))
      clazz._log.log_d('sanitized_env_path={}'.format(sanitized_env_path))
      clazz._log.log_d('            result={}'.format(result))
      clazz._all_exes_cache[sanitize_path] = sorted(result, key = lambda exe: clazz.semantic_version(exe)._tokens, reverse = True)
    return clazz._all_exes_cache[sanitize_path]

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
