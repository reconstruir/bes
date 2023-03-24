#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.version.semantic_version import semantic_version
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from ..attr.bf_attr_value import bf_attr_value

from .bf_metadata_error import bf_metadata_error
from .bf_metadata_key import bf_metadata_key

class bf_metadata_handler(namedtuple('bf_metadata_handler', 'key, getter, decoder, encoder, checker, old_getter')):

  def __new__(clazz, key, getter, decoder, encoder, checker, old_getter):
    key = check.check_bf_metadata_key(key)
    check.check_callable(getter)
    check.check_callable(decoder)
    check.check_callable(encoder)
    check.check_checker(checker)
    check.check_callable(old_getter, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, key, getter, decoder, encoder, checker, old_getter)

  @cached_property
  def attr_value(self):
    return bf_attr_value(self.key.as_string, self.decoder, self.encoder, self.checker)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def get(self, filename):
    return self.getter(filename)

  def decode(self, value):
    return self.decoder(value)

  def encode(self, value):
    return self.encoder(value)
  
  def check(self, value):
    return self.checker(value)
  
check.register_class(bf_metadata_handler, include_seq = False, cast_func = bf_metadata_handler._check_cast_func)
