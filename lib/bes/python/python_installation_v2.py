#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import re

from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.system.host import host
from bes.system.log import logger
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
    python_exe.check_exe(exe)

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
      host.raise_unsupported_system(system = system)
    if not result:
      assert message
      raise python_error('Failed to determine python for "{}" - {}'.format(exe, message))
    return result

  _WINDOWS_PYTHON_EXTENSIONS = ( 'exe', 'bat', 'cmd' )
  def _exe_basename_version(clazz, exe_type, basename):
    if filename_util.has_any_extension(basename, clazz._WINDOWS_PYTHON_EXTENSIONS, ignore_case = True):
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
    exe_type, exe_version = clazz._identify_exe(exe)
    if not exe_type:
      return None, 'exe is neither python or pip: "{}"'.format(exe)
    clazz._log.log_d('_determine_stuff_windows: exe_type={} exe_version={}'.format(exe_type, exe_version))

    root_dir = path.dirname(exe)
    
    if exe_type == 'pip':
      vi = python_pip_exe.version_info(exe)
      clazz._log.log_d('_determine_stuff_windows: pip version_info={}'.format(vi))
      py_version = vi.python_version
    elif exe_type == 'python':
      py_version = python_exe.version(exe)
    clazz._log.log_d('_determine_stuff_windows: exe={}'.format(exe))
    clazz._log.log_d('_determine_stuff_windows: root_dir={}'.format(root_dir))
    clazz._log.log_d('_determine_stuff_windows: py_version={}'.format(py_version))

    py_major_version = python_version.major_version(py_version)

    possible_pythons = []
    for ext in clazz._WINDOWS_PYTHON_EXTENSIONS:
      possible_pythons.append(path.join(root_dir, 'python.{}'.format(ext)))

    possible_pips = []
    for ext in clazz._WINDOWS_PYTHON_EXTENSIONS:
      possible_pips.extend([
        path.join(root_dir, 'Scripts', 'pip{}.{}'.format(py_version, ext)),
        path.join(root_dir, 'Scripts', 'pip{}.{}'.format(py_major_version, ext)),
        path.join(root_dir, 'Scripts', 'pip.{}'.format(ext)),
    ])
      
    py_exe = clazz._find_possible_exe(possible_pythons)
    pip_exe = clazz._find_possible_exe(possible_pips)
    clazz._log.log_d('_determine_stuff_windows: py_exe={} pip_exe={}'.format(py_exe, pip_exe))
    return clazz._stuff(root_dir, py_exe, pip_exe, py_version), None
  
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
    clazz._log.log_d('_determine_stuff_macos: py_exe={} pip_exe={}'.format(py_exe, pip_exe))
    return clazz._stuff(root_dir, py_exe, pip_exe, py_version), None

  def _find_possible_exe(clazz, possible_exes):
    for p in possible_exes:
      if path.exists(p):
        return p
    return None
  
  def _determine_stuff_linux(clazz, exe):
    assert False

  @cached_property
  def PATH(self):
    if self.system in ( host.LINUX, host.MACOS ):
      return [ path.dirname(self.python_exe) ]
    elif self.system == host.WINDOWS:
      return [
        path.dirname(self.python_exe),
        path.dirname(self.pip_exe),
      ]

  @cached_property
  def PYTHONPATH(self):
    return python_exe.site_packages_path(self.python_exe)

  @cached_property
  def windows_versioned_install_dirname(self):
    parsed_version = python_version.parse(self.python_version)
    return 'Python{}{}'.format(parsed_version.major,
                               parsed_version.minor)
