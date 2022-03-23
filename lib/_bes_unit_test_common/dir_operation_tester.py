#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_find import file_find
from bes.fs.testing.temp_content import temp_content
from bes.property.cached_property import cached_property

class dir_operation_tester(object):

  def __init__(self,
               multiplied_content_items = None,
               content_multiplier = 1,
               extra_content_items = None,
               dst_dir_same_as_src = False):
    self._multiplied_content_items = multiplied_content_items
    self._content_multiplier = content_multiplier
    self._extra_content_items = extra_content_items
    self._dst_dir_same_as_src = dst_dir_same_as_src

    self.dst_dirs = []
    self.src_dirs = []
    self.dst_files = []
    self.src_files = []
    self.src_files_before = []
    self._result = None
    
  @cached_property
  def tmp_dir(self):
    return temp_content.write_multiplied_items_to_temp_dir(multiplied_content_items = self._multiplied_content_items,
                                                           content_multiplier = self._content_multiplier,
                                                           extra_content_items = self._extra_content_items)

  @cached_property
  def src_dir(self):
    return path.join(self.tmp_dir, 'src')
    
  @cached_property
  def dst_dir(self):
    if self._dst_dir_same_as_src:
      dst_dir = self.src_dir
    else:
      dst_dir = path.join(self.tmp_dir, 'dst')
    return dst_dir

  def __enter__(self):
    if path.exists(self.src_dir):
      self.src_files_before = file_find.find(self.src_dir, relative = True, file_type = file_find.ANY)
    else:
      self.src_files_before = []
    return self
  
  def __exit__(self, type, value, traceback):
    if path.exists(self.src_dir):
      self.src_files = file_find.find(self.src_dir, relative = True, file_type = file_find.ANY)
      self.src_dirs = file_find.find(self.src_dir, relative = True, file_type = file_find.DIR)
    else:
      self.src_files = []
      self.src_dirs = []
    if path.exists(self.dst_dir):
      self.dst_files = file_find.find(self.dst_dir, relative = True, file_type = file_find.ANY)
      self.dst_dirs = file_find.find(self.dst_dir, relative = True, file_type = file_find.DIR)
    else:
      self.dst_files = []
      self.dst_dirs = []

  @property
  def result(self):
    if self._result == None:
      raise RuntimeError('result has not been set')
    return self._result

  @result.setter
  def result(self, result):
    self._result = result
  
