#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check
from bes.common.type_checked_list import type_checked_list
from bes.compat.StringIO import StringIO
from bes.property.cached_property import cached_property

from .vfs_error import vfs_error
from .vfs_list_options import vfs_list_options
from .vfs_path import vfs_path

class vfs_file_info(namedtuple('vfs_file_info', 'dirname, basename, ftype, size, checksum, attributes, children')):

  FILE = 'file'
  DIR = 'dir'
  
  def __new__(clazz, dirname, basename, ftype, size = None, checksum = None, attributes = None, children = None):
    check.check_string(dirname)
    check.check_string(basename)
    check.check_string(ftype)
    check.check_int(size, allow_none = True)
    check.check_string(checksum, allow_none = True)
    check.check_dict(attributes, allow_none = True)
    check.check_vfs_file_info_list(children, entry_type = vfs_file_info, allow_none = True)

    children = children or vfs_file_info_list()
    
    if ftype == clazz.FILE:
      if children:
        raise vfs_error('children is only for "dir"')
    if ftype == clazz.DIR:
      if size:
        raise vfs_error('size is only for "file"')
      if checksum:
        raise vfs_error('checksum is only for "file"')
      if attributes:
        raise vfs_error('attributes are only for "file"')
    return clazz.__bases__[0].__new__(clazz, dirname, basename, ftype, size, checksum, attributes, children)

  def __iter__(self):
    return iter(self.children)

#  def __str__(self):
#    return self.to_string()

  @property
  def filename(self):
    return vfs_path.normalize(vfs_path.join(vfs_path.ensure_lsep(self.dirname),
                                            vfs_path.lstrip_sep(self.basename)))

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
    options = options or vfs_list_options()
    buf = StringIO()
    self._entry_to_string(self, buf, options, 0)
    return buf.getvalue()

  @classmethod
  def _entry_to_string(clazz, entry, buf, options, depth):
    indent = '  ' * depth
    if entry.ftype == 'file':
      if options.show_details:
        buf.write('{}{} {} {} {}'.format(indent, entry.display_filename, entry.ftype, entry.size, entry.checksum))
        clazz._write_attributes(entry, buf)
      else:
        buf.write('{}{}'.format(indent, entry.display_filename))
      buf.write('\n')
    elif entry.ftype == 'dir':
      for child in entry:
        if options.show_details:
          buf.write('{}{} {} {} {}'.format(indent, child.display_filename, child.ftype, child.size, child.checksum))
          clazz._write_attributes(child, buf)
        else:
          buf.write('{}{}'.format(indent, child.display_filename))
          
        buf.write('\n')
        if child.is_dir():
          clazz._entry_to_string(child, buf, options, depth + 1)
  
  @classmethod
  def _write_attributes(clazz, info, buf):
    if info.attributes:
      for key, value in sorted(info.attributes.items()):
        buf.write(' {}={}'.format(key, value))
  
check.register_class(vfs_file_info, include_seq = False)

class vfs_file_info_list(type_checked_list):

  __value_type__ = vfs_file_info
  
  def __init__(self, values = None):
    super(vfs_file_info_list, self).__init__(values = values)

  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    for vfs_file_info in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(vfs_file_info))
    return buf.getvalue()
  
  def __str__(self):
    return self.to_string()
  
check.register_class(vfs_file_info_list, include_seq = False)
