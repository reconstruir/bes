#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
import sys

from bes.system.check import check

class hash_util(object):
  'Hash util'

  @classmethod
  def hash_string_sha256(clazz, s, encoding = 'utf-8'):
    'Return true if the given object can be encoded as json.'
    check.check_string(s)
    
    return hashlib.sha256(s.encode(encoding)).hexdigest()

  @classmethod
  def hash_string_unsigned(clazz, s, num_digits = None):
    check.check_string(s)

    h = int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16)
    if num_digits == None:
      return h
    return h % (10 ** num_digits)
