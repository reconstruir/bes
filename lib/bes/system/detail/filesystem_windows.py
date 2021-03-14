#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import ctypes
import os
import platform
import sys

from .filesystem_base import filesystem_base

from bes.system.execute import execute

class filesystem_windows(filesystem_base):

  @classmethod
  #@abstractmethod
  def free_disk_space(clazz, directory):
    'Return the free space for directory in bytes.'
    bytes_free = ctypes.c_ulonglong(0)
    native_directory = ctypes.c_wchar_p(directory)
    bytes_free_pointer = ctypes.pointer(bytes_free)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(native_directory, None, None, bytes_free_pointer)
    return bytes_free.value

  @classmethod
  #@abstractmethod
  def sync(clazz):
    'Sync the filesystem.'
    # FIXME: needs windows impl
    pass
