#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.compat.StringIO import StringIO

from .fs_error import fs_error
from .fs_list_options import fs_list_options

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

  def __str__(self):
    return self.to_string()

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

  def to_string(self, options = None):
    options = options or fs_list_options()
    buf = StringIO()
    self._entry_to_string(self, buf, options, 0)
    return buf.getvalue()

  @classmethod
  def _entry_to_string(clazz, entry, buf, options, depth):
    indent = '  ' * depth
    if entry.ftype == 'file':
      if options.show_details:
        buf.write('{}{} {} {} {} {}'.format(indent, entry.display_filename, entry.ftype, entry.size, entry.checksum, entry.attributes))
      else:
        buf.write('{}{}'.format(indent, entry.display_filename))
      buf.write('\n')
    elif entry.ftype == 'dir':
      for child in entry:
        if options.show_details:
          buf.write('{}{} {} {} {} {}'.format(indent, child.display_filename, child.ftype, child.size, child.checksum, child.attributes))
        else:
          buf.write('{}{}'.format(indent, child.display_filename))
          
        buf.write('\n')
        if child.is_dir():
          clazz._entry_to_string(child, buf, options, depth + 1)
  
check.register_class(fs_file_info, include_seq = False)
