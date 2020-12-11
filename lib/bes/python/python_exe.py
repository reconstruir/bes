#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os, sys

from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.file_symlink import file_symlink
from bes.system.execute import execute
from bes.system.host import host
from bes.system.which import which
from bes.system.os_env import os_env_var
from bes.version.software_version import software_version

from bes.unix.brew.brew import brew

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
  def source(clazz, exe):
    '''Return the source of the python executable.  One of:
          brew: brew (macos or linux)
    python.org: python.org (macos)
        system: builtin to system (macos or linux)
       unknown: none of the above
         xcode: part of xcode
    '''
    clazz.check_exe(exe)

    if clazz._source_is_xcode(exe):
      return 'xcode'
    if clazz._source_is_system(exe):
      return 'system'
    elif clazz._source_is_brew(exe):
      return 'brew'
    elif clazz._source_is_python_org(exe):
      return 'python.org'
    else:
      return 'unknown'
    
  @classmethod
  def _source_is_brew(clazz, exe):
    'Return True if python executable is from brew'

    if not brew.has_brew():
      return False
    
    if host.is_macos():
      actual_exe = file_symlink.resolve(exe)
      return 'cellar' in actual_exe.lower()
    else:
      host.raise_unsupported_system()

  @classmethod
  def _source_is_xcode(clazz, exe):
    'Return True if python executable is from brew'

    real_exe = clazz.sys_executable(exe)
    return 'Applications/Xcode.app' in real_exe
      
  @classmethod
  def _source_is_system(clazz, exe):
    'Return True if the given python executable came builtin to the current system'

    if host.is_macos():
      return exe.lower().startswith('/usr/bin/python')
    elif host.is_linux():
      return exe.lower().startswith('/usr/bin/python')
    else:
      host.raise_unsupported_system()

  @classmethod
  def _source_is_python_org(clazz, exe):
    'Return True if the given python executable is from python.org'

    return False
      
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

  @classmethod
  def sys_executable(clazz, exe):
    'Return the value of sys.executable for the given python executable'
    clazz.check_exe(exe)

    script = '''\
import sys
assert len(sys.argv) == 2
_filename = sys.argv[1]
with open(_filename, 'w') as f:
  f.write(sys.executable)
raise SystemExit(0)
'''
    tmp_script = temp_file.make_temp_file(content = script, suffix = '.py')
    tmp_output = temp_file.make_temp_file()
    cmd = [ exe, tmp_script, tmp_output ]
    rv = execute.execute(cmd)
    return file_util.read(tmp_output).strip()

  _python_exe_info = namedtuple('_python_exe_info', 'exe, version, full_version, source, real_exe, exe_links')
  @classmethod
  def info(clazz, exe):
    'Return info for python executables'
    clazz.check_exe(exe)

    main_exe, exe_links = clazz._determine_main_exe_and_links(exe)
    return clazz._python_exe_info(main_exe,
                                  clazz.version(main_exe),
                                  clazz.full_version(main_exe),
                                  clazz.source(main_exe),
                                  clazz.sys_executable(main_exe),
                                  exe_links)

  @classmethod
  def _determine_main_exe_and_links(clazz, exe):
    'Return info for python executables'
    inode = file_util.inode_number(exe)
    exes = clazz._find_python_exes_in_PATH()
    inode_map = clazz._inode_map(exes)
    if not inode in inode_map:
      return exe, []
    links = inode_map[inode]
    main_exe = links.pop(0)
    return main_exe, links
  
  @classmethod
  def find_python_exes(clazz):
    'Return all the executables in PATH that match any patterns'
    all_exes = clazz._find_python_exes_in_PATH()
    inode_map = clazz._inode_map(all_exes)
    result = []
    for inode, exes in inode_map.items():
      main_exe = exes.pop(0)
      result.append(main_exe)
    return result

  @classmethod
  def _find_python_exes_in_PATH(clazz):
    'Return all the executables in PATH that match any patterns'
    patterns = [
      'python',
      'python2',
      'python2.?',
      'python3',
      'python3.?',
    ]
    return file_path.glob(os_env_var('PATH').path, patterns)
  
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
  
