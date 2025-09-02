#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.compat import url_compat
from bes.files.bf_path import bf_path
from bes.fs.file_symlink import file_symlink
from bes.fs.file_util import file_util
from bes.python.python_script import python_script
from bes.version.semantic_version import semantic_version

from bes.files.bf_glob import bf_glob

from .python_source_unix import python_source_unix

class python_source_macos(python_source_unix):

  @classmethod
  #@abstractmethod
  def exe_source(self, exe):
    'Return the source of the python executable.  Stuff like brew, xcode, system, python.org.'
    if self._source_is_xcode(exe):
      return 'xcode'
    elif self._source_is_unix_system(exe):
      return 'system'
    elif self._source_is_brew(exe):
      return 'brew'
    else:
      return 'unknown'

  @classmethod
  #@abstractmethod
  def possible_python_bin_dirs(self):
    'Return a list of possible dirs where the python executable might be.'
    result = []
    brew_pythons = bf_glob.glob('/usr/local/opt/', 'python@?.*/bin')
    sorted_brew_pythons = semantic_version.sort_string_list(brew_pythons, reverse = True)
    result.extend(sorted_brew_pythons)
    brew_pythons = bf_glob.glob('/usr/local/opt/', 'python@?/bin')
    sorted_brew_pythons = semantic_version.sort_string_list(brew_pythons, reverse = True)
    result.extend(sorted_brew_pythons)
    result.extend([
      '/opt/local/bin',
      '/usr/bin',
      '/usr/local/bin',
    ])
    return result
  
  @classmethod
  def _source_is_xcode(clazz, exe):
    'Return True if python executable is from brew'
    real_exe = python_script.sys_executable(exe)
    return 'Applications/Xcode.app' in real_exe

  @classmethod
  def _source_is_brew(clazz, exe):
    'Return True if python executable is from brew'
    
    # First check the exe itself to see if its in the brew "cellar"
    actual_exe = file_symlink.resolve(exe)
    if 'cellar' in actual_exe.lower():
      return True

    # Next check the exe prefix standard to brew to check if that is in the brew "cellar"
    if actual_exe.startswith('/usr/local/opt/python@'):
      parts = file_path.split(actual_exe)
      prefix = file_path.join(parts[0:5])
      actual_prefix = file_symlink.resolve(prefix)
      if 'cellar' in actual_prefix.lower():
        return True
    return False

  @classmethod
  #@abstractmethod
  def possible_python_dot_org_installer_filenames(self, full_version):
    'Return a list of possible python.org installer filenames for full version.'
    check.check_python_version(full_version)

    template = '{full_version}/python-{full_version}-macosx10.9.pkg'
    return [ template.format(full_version = full_version) ]
  
