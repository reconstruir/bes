#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common.check import check

class fs_file_info(namedtuple('fs_file_info', 'filename, size, checksum, attributes')):

  def __new__(clazz, filename, size, checksum, attributes):
    check.check_string(filename)
    check.check_string(checksum)
    check.check_int(size)
    check.check_dict(attributes, check.STRING_TYPES, check.STRING_TYPES)
    return clazz.__bases__[0].__new__(clazz, filename, size, checksum, attributes)

check.register_class(fs_file_info, include_seq = False)
