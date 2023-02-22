#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.tuple_util import tuple_util

class bfile_attr_value(namedtuple('bfile_attr_value', 'key, decoder, encoder, checker, old_keys')):

  def __new__(clazz, key, decoder, encoder, checker, old_keys):
    check.check_string(key)
    check.check_callable(decoder)
    check.check_callable(encoder)
    check.check_callable(checker)
    check.check_string_seq(old_keys, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, key, decoder, encoder, checker, old_keys)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def decode(self, value):
    return self.decoder(value)

  def encode(self, value):
    return self.encoder(value)

  def check(self, value):
    return self.checker(value)
  
check.register_class(bfile_attr_value, include_seq = False, cast_func = bfile_attr_value._check_cast_func)
