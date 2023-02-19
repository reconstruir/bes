#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
import sys

from bes.system.check import check

class hash_util(object):
  'Hash util'

  @classmethod
  def hash_string_md5(clazz, s, encoding = 'utf-8'):
    'Return true if the given object can be encoded as json.'
    check.check_string(s)
    check.check_string(s, encoding)
    
    return hashlib.md5(s.encode(encoding)).hexdigest()
  
  @classmethod
  def hash_string_sha1(clazz, s, encoding = 'utf-8'):
    'Return true if the given object can be encoded as json.'
    check.check_string(s)
    check.check_string(s, encoding)
    
    return hashlib.sha1(s.encode(encoding)).hexdigest()

  @classmethod
  def hash_string_sha256(clazz, s, encoding = 'utf-8'):
    'Return true if the given object can be encoded as json.'
    check.check_string(s)
    check.check_string(s, encoding)
    
    return hashlib.sha256(s.encode(encoding)).hexdigest()

  @classmethod
  def hash_string_unsigned(clazz, s, num_digits = None):
    check.check_string(s)
    check.check_int(num_digits, allow_none = True)

    h = int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16)
    if num_digits == None:
      return h
    return h % (10 ** num_digits)

  @classmethod
  def hash_string_zfilled(clazz, s, num_digits = None):
    check.check_string(s)
    check.check_int(num_digits, allow_none = True)

    hs = str(clazz.hash_string_unsigned(s, num_digits = num_digits))
    if num_digits == None:
      return hs
    return hs.zfill(num_digits)
