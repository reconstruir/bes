#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import re

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.system.host import host
from bes.system.log import logger
from bes.system.os_env import os_env
from bes.fs.file_mime import file_mime
from bes.fs.file_path import file_path
from bes.fs.filename_util import filename_util

from .python_error import python_error
from .python_exe import python_exe
from .python_pip_exe import python_pip_exe
from .python_version import python_version

class python_installation_v2(object):
  'Class to determine the filename and directory values of a pip installatiuon.'

  _log = logger('python')
  
  def __init__(self, exe, system = None):
    check.check_string(exe)
    check.check_string(system, allow_none = True)

    self.system = system or host.SYSTEM
    
    if not path.isabs(exe):
      raise python_error('exe should be an absolute path: "{}"'.format(exe))
    if not path.exists(exe):
      raise python_error('exe does not exist: "{}"'.format(exe))
    if not file_path.is_executable(exe):
      raise python_error('exe is not executable: "{}"'.format(exe))
    
    stuff = self._determine_stuff(exe, system = self.system)
    self.root_dir = stuff.root_dir
    self.python_exe = stuff.python_exe
    self.pip_exe = stuff.pip_exe
    self.python_version = stuff.python_version

  def __str__(self):
    return "<{} root_dir={} python_exe={} pip_exe={} python_version={}>".format(
      self.__class__.__name__,
      self.root_dir,
      self.python_exe,
      self.pip_exe,
      self.python_version)

  _stuff = namedtuple('_stuff', 'root_dir, python_exe, pip_exe, python_version')
  def _determine_stuff(clazz, exe, system):
    if system == host.WINDOWS:
      result, message = clazz._determine_stuff_windows(exe)
    elif system == host.MACOS:
      result, message = clazz._determine_stuff_macos(exe)
    elif system == host.LINUX:
      result, message = self._determine_stuff_linux(exe)
    else:
      host.raise_unsupported_system()
    if not result:
      assert message
      raise python_error('Failed to determine python for "{}" - {}'.format(exe, message))
    return result

  def _exe_basename_version(clazz, exe_type, basename):
    if filename_util.has_any_extension(basename, ( 'exe', 'bat', 'cmd', 'ps1' ), ignore_case = True):
      root = filename_util.without_extension(basename)
    else:
      root = basename
    f = re.findall(r'^{}(\d.*)$'.format(exe_type), root)
    if not f:
      return None
    return f[0]
  
  _exe_info = namedtuple('_stuff', 'exe_type, version')
  def _identify_exe(clazz, exe):
    basename = path.basename(exe).lower()
    if basename.startswith('pip'):
      exe_type = 'pip'
      version = clazz._exe_basename_version(exe_type, basename)
      return clazz._exe_info(exe_type, version)
    elif basename.startswith('python'):
      exe_type = 'python'
      version = clazz._exe_basename_version(exe_type, basename)
      return clazz._exe_info(exe_type, version)
    return clazz._exe_basename_version(None, None)
  
  def _determine_stuff_windows(clazz, exe):
    exe_type = clazz._identify_exe(exe)
    if not exe_type:
      return None, 'exe is neither python or pip: "{}"'.format(exe)
    if exe_type == 'pip':
      pass
    elif exe_type == 'python':
      pass
    assert False

  def _determine_stuff_macos(clazz, exe):
    exe_type, exe_version = clazz._identify_exe(exe)
    if not exe_type:
      return None, 'exe is neither python or pip: "{}"'.format(exe)
    clazz._log.log_d('_determine_stuff_macos: exe_type={} exe_version={}'.format(exe_type, exe_version))

    bin_dir = path.dirname(exe)
    
    if exe_type == 'pip':
      vi = python_pip_exe.version_info(exe)
      clazz._log.log_d('_determine_stuff_macos: pip version_info={}'.format(vi))
      py_version = vi.python_version
    elif exe_type == 'python':
      py_version = python_exe.version(exe)
    clazz._log.log_d('_determine_stuff_macos: exe={}'.format(exe))
    clazz._log.log_d('_determine_stuff_macos: bin_dir={}'.format(bin_dir))
    clazz._log.log_d('_determine_stuff_macos: py_version={}'.format(py_version))

    py_major_version = python_version.major_version(py_version)

    possible_pythons = [
      path.join(bin_dir, 'python{}'.format(py_version)),
      path.join(bin_dir, 'python{}'.format(py_major_version)),
    ]

    possible_pips = [
      path.join(bin_dir, 'pip{}'.format(py_version)),
      path.join(bin_dir, 'pip{}'.format(py_major_version)),
    ]

    py_exe = clazz._find_possible_exe(possible_pythons)
    pip_exe = clazz._find_possible_exe(possible_pips)
    
    root_dir = path.normpath(path.join(bin_dir, '..'))
    return clazz._stuff(root_dir, py_exe, pip_exe, py_version), None

  def _find_possible_exe(clazz, possible_exes):
    for p in possible_exes:
      if path.exists(p):
        return p
    return None
  
  def _determine_stuff_linux(clazz, exe):
    pass
  
  @cached_property
  def pip_exe(self):
    'Return the pip executable'
    if self._system == host.WINDOWS:
      pip_exe_basename = 'pip{}.exe'.format(self._python_version)
      python_dir = 'Python{}'.format(self._python_version.replace('.', ''))
      if self._python_version == '2.7':
        pexe = path.join(self._root_dir, 'Scripts', pip_exe_basename)
      else:
        pexe = path.join(self._root_dir, python_dir, 'Scripts', pip_exe_basename)
    elif self._system in ( host.LINUX, host.MACOS ):
      pip_exe_basename = 'pip{}'.format(self._python_version)
      pexe = path.join(self._root_dir, 'bin', pip_exe_basename)
    else:
      host.raise_unsupported_system()
    return pexe
    
    return self._pip_exe

  @cached_property
  def bin_dir(self):
    'Return the bin dir'
    if self._system == host.WINDOWS:
      python_dir = 'Python{}'.format(self._python_version.replace('.', ''))
      if self._python_version == '2.7':
        bin_dir = path.join(self._root_dir, 'Scripts')
      else:
        bin_dir = path.join(self._root_dir, python_dir, 'Scripts')
    elif self._system in ( host.LINUX, host.MACOS ):
      bin_dir = path.join(self._root_dir, 'bin')
    else:
      host.raise_unsupported_system()
    return bin_dir
  
  @cached_property
  def site_packages_dir(self):
    'Return the pip site-packages dir sometimes needed for PYTHONPATH'
    if self._system == host.WINDOWS:
      python_dir = 'Python{}'.format(self._python_version.replace('.', ''))
      site_packaged_dir = path.join(self._root_dir, python_dir, 'site-packages')
    elif self._system in ( host.LINUX, host.MACOS ):
      site_packaged_dir = path.join(self._root_dir, 'lib/python/site-packages')
    else:
      host.raise_unsupported_system()
    return site_packaged_dir

  @cached_property
  def PYTHONPATH(self):
    return [ self.site_packages_dir ]

  @cached_property
  def PATH(self):
    return [ self.bin_dir ]

  x = '''
  @classmethod
  def find_root_dir(clazz, pip_exe, system = None):
    'Find the install dir from the pip exe'
    check.check_string(pip_exe)

    if self._system == host.WINDOWS:
      result = self._find_root_dir_windows(pip_exe)
    elif self._system in ( host.LINUX, host.MACOS ):
      result = self._find_root_dir_unix(pip_exe)
    else:
      host.raise_unsupported_system()
    return result

  @classmethod
  def _find_root_dir_unix(clazz, pip_exe):
    return path.normpath(path.join(path.dirname(pip_exe), '..'))
  
  @classmethod
  def _find_root_dir_windows(clazz, pip_exe):
    basename = path.basename(pip_exe)

    f = re.findall(r'^pip(\d+\.\d+)\....$', basename, flags = re.IGNORECASE)
    if not f:
      raise python_error('pip_exe does not contain a python version: "{}"'.format(pip_exe))
    if len(f) != 1:
      raise python_error('pip_exe does not contain a python version: "{}"'.format(pip_exe))
    python_version = f[0]
    parent_dir = file_path.parent_dir(pip_exe)

    if python_version == '2.7':
      result = file_path.parent_dir(parent_dir)
    else:
      result = file_path.parent_dir(parent_dir)
      
    
    return 'caca'
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
'''  
