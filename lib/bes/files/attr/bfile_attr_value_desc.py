#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.common.tuple_util import tuple_util

from .bfile_attr_error import bfile_attr_error

class bfile_attr_value_desc(namedtuple('bfile_attr_value_desc', 'key, decoder, encoder')):

  def __new__(clazz, key, decoder, encoder):
    check.check_string(key)
    check.check_callable(decoder)
    check.check_callable(encoder)

    return clazz.__bases__[0].__new__(clazz, key, decoder, encoder)

  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def decode(self, value):
    return self.decoder(value)

  def encode(self, value):
    return self.encoder(value)
  
check.register_class(bfile_attr_value_desc, include_seq = False, cast_func = bfile_attr_value_desc._check_cast_func)
