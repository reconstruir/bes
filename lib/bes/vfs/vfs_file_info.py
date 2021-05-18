#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

from collections import namedtuple
from datetime import datetime

from bes.common.check import check
from bes.common.type_checked_list import type_checked_list
from bes.compat.StringIO import StringIO
from bes.property.cached_property import cached_property
from bes.fs.checksum_set import checksum_set

from .vfs_error import vfs_error
from .vfs_list_options import vfs_list_options
from .vfs_path_util import vfs_path_util

class vfs_file_info(namedtuple('vfs_file_info', 'filename, ftype, modification_date, size, checksums, attributes, children')):

  FILE = 'file'
  DIR = 'dir'
  SEP = '/'
  
  def __new__(clazz, filename, ftype, modification_date, size = None, checksums = None, attributes = None, children = None):
    check.check_string(filename)
    check.check_string(ftype)
    check.check(modification_date, datetime)
    check.check_int(size, allow_none = True)
    check.check_checksum_set(checksums, allow_none = True)
    check.check_dict(attributes, allow_none = True)
    check.check_vfs_file_info_list(children, entry_type = vfs_file_info, allow_none = True)
    
    filename = vfs_path_util.normalize(filename)
    
    if ftype == clazz.FILE:
      if children:
        raise vfs_error('children is only for "dir"')
      children = None
    if ftype == clazz.DIR:
      children = children or vfs_file_info_list()
      if size:
        raise vfs_error('size is only for "file"')
      if checksums:
        raise vfs_error('checksums is only for "file"')
      if attributes:
        raise vfs_error('attributes are only for "file"')
    return clazz.__bases__[0].__new__(clazz, filename, ftype, modification_date, size, checksums, attributes, children)

  def __iter__(self):
    return iter(self.children)

  @cached_property
  def dirname(self):
    return vfs_path_util.dirname(self.filename)

  @cached_property
  def basename(self):
    return vfs_path_util.basename(self.filename)

  @cached_property
  def parts(self):
    'The split parts of the filename path'
    return self.filename.split(self.SEP)
  
  @cached_property
  def display_filename(self):
    if self.ftype == self.DIR:
      return self.filename + self.SEP
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

  def to_dict(self, flatten_attributes = False, flatten_paths = False):
    chk = self.checksums.to_dict() if self.checksums else {}
    d = {
      'filename': self.filename,
      'ftype': self.ftype,
      'modification_date': str(self.modification_date),
      'size': self.size,
      'checksums': self.checksums.to_dict() if self.checksums else None,
    }
    if self.ftype == 'dir':
      if self.children:
        d['children'] = self.children.to_dict_list(flatten_attributes = flatten_attributes, flatten_paths = flatten_paths)
      else:
        d['children'] = []
    else:
      d['children'] = None
        
    if flatten_attributes:
      d.update(self.attributes)
    else:
      d['attributes'] = self.attributes
    return d
  
  @classmethod
  def _entry_to_string(clazz, entry, buf, options, depth):
    indent = '  ' * depth
    checksum_str = ''
    if entry.checksums:
      checksum_str = str(entry.checksums.preferred())
    if entry.ftype == 'file':
      if options.show_details:
        buf.write('{}{} {} {} {}'.format(indent, entry.display_filename, entry.ftype, entry.size, checksum_str))
        clazz._write_attributes(entry, buf)
      else:
        buf.write('{}{}'.format(indent, entry.display_filename))
      buf.write('\n')
    elif entry.ftype == 'dir':
      for child in entry:
        if options.show_details:
          buf.write('{}{} {} {} {}'.format(indent, child.display_filename, child.ftype, child.size, checksum_str))
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

  def to_dict_list(self, flatten_attributes = False, flatten_paths = False):
    return [ entry.to_dict(flatten_attributes = flatten_attributes, flatten_paths = flatten_paths) for entry in self ]
  
check.register_class(vfs_file_info_list, include_seq = False)
