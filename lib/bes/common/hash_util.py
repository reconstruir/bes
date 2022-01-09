#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib

class hash_util(object):
  'Hash util'

  @classmethod
  def hash_string_sha256(clazz, s, encoding = 'utf-8'):
    'Return true if the given object can be encoded as json.'
    return hashlib.sha256(s.encode(encoding)).hexdigest()
