#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

class checksum(namedtuple('checksum', 'algorithm, checksum')):

  SHA256 = 'sha256'
  SHA1 = 'sha1'
  MD5 = 'md5'
  
  def __new__(clazz, algorithm, checksum):
    check.check_string(algorithm)
    check.check_string(checksum)
    return clazz.__bases__[0].__new__(clazz, algorithm, checksum)

  def __str__(self):
    return '{}:{}'.format(self.algorithm, self.checksum)

  def __repr__(self):
    return str(self)

check.register_class(checksum, include_seq = False)
