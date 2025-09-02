#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import re

from bes.common.algorithm import algorithm
from ..system.check import check
from ..files.bf_entry import bf_entry
from bes.property.cached_property import cached_property
from bes.system.host import host
from bes.system.log import logger
from bes.fs.filename_util import filename_util

from .python_error import python_error
from .python_exe import python_exe
from .python_pip_exe import python_pip_exe
from .python_script import python_script
from .python_source import python_source
from .python_version import python_version

class python_installation(object):
  'Class to determine the filename and directory values of a python installatiuon.'

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
    if not bf_entry(exe).is_executable:
      raise python_error('exe is not executable: "{}"'.format(exe))
    
    stuff = self._determine_stuff(exe, system = self.system)
    self._log.log_d(f'stuff={stuff}')
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
    elif system in ( host.MACOS, host.LINUX ):
      result, message = clazz._determine_stuff_unix(exe)
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

  def exe_filename_version(clazz, exe_type, filename):
    name = python_source.exe_name(filename)
    f = re.findall(r'^{}(\d.*)$'.format(exe_type), name)
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
    clazz._log.log_d('_determine_stuff_windows: root_dir={}'.format(root_dir))
    
    if exe_type == 'pip':
      vi = python_pip_exe.version_info(exe)
      clazz._log.log_d('_determine_stuff_windows: pip version_info={}'.format(vi))
      py_version = vi.python_version
    elif exe_type == 'python':
      py_version = python_exe.version(exe)
    clazz._log.log_d('_determine_stuff_windows: exe={}'.format(exe))
    clazz._log.log_d('_determine_stuff_windows: root_dir={}'.format(root_dir))
    clazz._log.log_d('_determine_stuff_windows: py_version={}'.format(py_version))

    py_major_version = python_version(py_version).major_str

    possible_pythons = []
    for ext in clazz._WINDOWS_PYTHON_EXTENSIONS:
      possible_pythons.append(path.join(root_dir, 'python.{}'.format(ext)))

    possible_pips = []
    for ext in clazz._WINDOWS_PYTHON_EXTENSIONS:
      possible_pips.extend([
        path.join(root_dir, 'Scripts', 'pip{}.{}'.format(py_version, ext)),
        path.join(root_dir, 'Scripts', 'pip{}.{}'.format(py_major_version, ext)),
        path.join(root_dir, 'Scripts', 'pip.{}'.format(ext)),
        path.join(root_dir, 'pip{}.{}'.format(py_version, ext)),
        path.join(root_dir, 'pip{}.{}'.format(py_major_version, ext)),
        path.join(root_dir, 'pip.{}'.format(ext)),
    ])

    py_exe = clazz._find_possible_exe(possible_pythons)
    pip_exe = clazz._find_possible_exe(possible_pips)
    clazz._log.log_d('_determine_stuff_windows: py_exe={} pip_exe={}'.format(py_exe, pip_exe))
    return clazz._stuff(root_dir, py_exe, pip_exe, py_version), None
  
  def _determine_stuff_unix(clazz, exe):
    exe_type, exe_version = clazz._identify_exe(exe)
    if not exe_type:
      return None, 'exe is neither python or pip: "{}"'.format(exe)
    clazz._log.log_d('_determine_stuff_unix: exe_type={} exe_version={}'.format(exe_type, exe_version))

    bin_dir = path.dirname(exe)
    
    if exe_type == 'pip':
      vi = python_pip_exe.version_info(exe)
      clazz._log.log_d('_determine_stuff_unix: pip version_info={}'.format(vi))
      py_version = vi.python_version
    elif exe_type == 'python':
      py_version = python_exe.version(exe)
    clazz._log.log_d('_determine_stuff_unix: exe={}'.format(exe))
    clazz._log.log_d('_determine_stuff_unix: bin_dir={}'.format(bin_dir))
    clazz._log.log_d('_determine_stuff_unix: py_version={}'.format(py_version))

    py_major_version = python_version(py_version).major_version_str

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
    clazz._log.log_d('_determine_stuff_unix: py_exe={} pip_exe={}'.format(py_exe, pip_exe))
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
    possible_exes = [ self.python_exe, self.pip_exe ]
    return algorithm.unique([ path.dirname(exe) for exe in possible_exes if exe ])

  @cached_property
  def PYTHONPATH(self):
    return python_script.site_packages_path(self.python_exe)

  @cached_property
  def windows_versioned_install_dirname(self):
    version = python_version(self.python_version)
    return 'Python{}{}'.format(version.major, version.minor)
