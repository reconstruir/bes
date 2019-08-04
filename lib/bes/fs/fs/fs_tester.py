#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.temp_file import temp_file
from .fs_list_options import fs_list_options

class fs_tester(object):

  def __init__(self, fs):
    self.fs = fs

  def list_dir(self, *args):
    return self._call_fs('list_dir', *args)
    
  def has_file(self, *args):
    return self._call_fs('has_file', *args)
    
  def file_info(self, *args):
    return self._call_fs('file_info', *args)

  def remove_file(self, *args):
    return self._call_fs('remove_file', *args)

  def upload_file(self, *args):
    return self._call_fs('upload_file', *args)

  def download_file(self, *args):
    return self._call_fs('download_file', *args)

  def set_file_attributes(self, *args):
    return self._call_fs('set_file_attributes', *args)
    
  def _call_fs(self, func_name, *args):
    func = getattr(self.fs, func_name)
    options = fs_list_options(show_details = True)
    result = func(*args)
    if result is None:
      return None
    return result.to_string(options = options)
