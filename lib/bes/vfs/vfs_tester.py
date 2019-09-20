#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime

from bes.fs.temp_file import temp_file
from .vfs_list_options import vfs_list_options
from .vfs_file_info_options import vfs_file_info_options

class vfs_tester(object):

  MTIME = datetime(year = 1999, month = 1, day = 1, hour = 1, minute = 1, second = 1)
  OPTIONS = vfs_file_info_options(hardcode_modification_date = MTIME)
  
  def __init__(self, fs):
    self.fs = fs

  def list_dir(self, *args):
    return self._call_fs('list_dir', True, *args)
    
  def has_file(self, *args):
    return self._call_fs('has_file', True, *args)
    
  def file_info(self, *args):
    return self._call_fs('file_info', True, *args)

  def remove_file(self, *args):
    return self._call_fs('remove_file', True, *args)

  def upload_file(self, *args):
    return self._call_fs('upload_file', True, *args)

  def download_to_file(self, *args):
    return self._call_fs('download_to_file', True, *args)

  def download_to_bytes(self, *args):
    return self._call_fs('download_to_bytes', False, *args)

  def set_file_attributes(self, *args):
    return self._call_fs('set_file_attributes', True, *args)
    
  def _call_fs(self, func_name, to_string, *args):
    func = getattr(self.fs, func_name)
    options = vfs_list_options(show_details = True)
    result = func(*args)
    if result is None:
      return None
    if to_string:
      return result.to_string(options = options)
    return result
