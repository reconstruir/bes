#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_symlink import file_symlink
from bes.fs.file_util import file_util
from bes.python.python_script import python_script
from bes.unix.brew.brew import brew

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
    return [
      '/opt/local/bin',
      '/usr/bin',
      '/usr/local/bin',
      '/usr/local/opt/python@3.7/bin',
      '/usr/local/opt/python@3.8/bin',
      '/usr/local/opt/python@3.9/bin',
    ]

  @classmethod
  def _source_is_xcode(clazz, exe):
    'Return True if python executable is from brew'
    real_exe = python_script.sys_executable(exe)
    return 'Applications/Xcode.app' in real_exe

  @classmethod
  def _source_is_brew(clazz, exe):
    'Return True if python executable is from brew'
    
    if not brew.has_brew():
      return False

    # This is slighlty faster than checking inodes, but it does
    # not always work depending on the python version and perhaps
    # whether its the main one
    actual_exe = file_symlink.resolve(exe)
    if 'cellar' in actual_exe.lower():
      return True

    # Check if the inode for exe matches a file in a python package in brew.
    # Checking the inode deals with links, indirection and other tricks
    # brew does to obfuscate the real exe
    exe_inode = file_util.inode_number(exe)
    b = brew()
    packages = b.installed()
    python_packages = [ p for p in packages if p.startswith('python@') ]
    for next_package in python_packages:
      files = b.files(next_package)
      for f in files:
        next_file_inode = file_util.inode_number(f)
        if exe_inode == next_file_inode:
          return True
    return False
