#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from ..system.check import check

from .checksum import checksum

class checksum_set(object):

  _PREFERRED = (
    checksum.SHA256,
    checksum.SHA1,
    checksum.MD5,
  )
  
  def __init__(self, *args):
    self._checksums = {}
    for arg in args:
      self.add(arg)
    
  def __str__(self):
    return ';'.join([ str(c) for c in self.to_list()])
  
  def __repr__(self):
    return str(self)
  
  def add(self, checksum):
    check.check_checksum(checksum)
    self._checksums[checksum.algorithm] = checksum

  def to_list(self):
    return [ c for _, c in sorted(self._checksums.items()) ]

  def to_dict(self):
    result = {}
    for _, checksum in self._checksums.items():
      result[checksum.algorithm] = ( checksum.algorithm, checksum.checksum )
    return result

  def preferred(self):
    for p in self._PREFERRED:
      n = self._checksums.get(p)
      if n:
        return n
    return None

check.register_class(checksum_set, include_seq = False)
