#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common.check import check

class fs_file_info(namedtuple('fs_file_info', 'filename, ftype, size, checksum, attributes')):

  FILE = 'file'
  DIR = 'dir'
  
  def __new__(clazz, filename, ftype, size, checksum, attributes):
    check.check_string(filename)
    check.check_string(ftype)
    check.check_int(size, allow_none = True)
    check.check_string(checksum, allow_none = True)
    check.check_dict(attributes, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, filename, ftype, size, checksum, attributes)

check.register_class(fs_file_info, include_seq = False)
