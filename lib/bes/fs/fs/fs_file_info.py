#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common.check import check
from bes.property.cached_property import cached_property

from .fs_error import fs_error

class fs_file_info(namedtuple('fs_file_info', 'filename, ftype, size, checksum, attributes, children')):

  FILE = 'file'
  DIR = 'dir'
  
  def __new__(clazz, filename, ftype, size, checksum, attributes, children):
    check.check_string(filename)
    check.check_string(ftype)
    check.check_int(size, allow_none = True)
    check.check_string(checksum, allow_none = True)
    check.check_fs_file_info_list(children, entry_type = fs_file_info)
    if ftype == clazz.FILE:
      if children:
        raise fs_error('children is only for "dir"')
    if ftype == clazz.DIR:
      if size:
        raise fs_error('size is only for "file"')
      if checksum:
        raise fs_error('checksum is only for "file"')
      if attributes:
        raise fs_error('attributes area only for "file"')
    return clazz.__bases__[0].__new__(clazz, filename, ftype, size, checksum, attributes, children)

  def __iter__(self):
    return iter(self.children)

  @cached_property
  def display_filename(self):
    if self.ftype == self.DIR:
      return self.filename + '/'
    elif self.ftype == self.FILE:
      return self.filename
    else:
      assert False
  
  def is_dir(self):
    return self.ftype == self.DIR
  
  def is_file(self):
    return self.ftype == self.FILE
  
check.register_class(fs_file_info, include_seq = False)
