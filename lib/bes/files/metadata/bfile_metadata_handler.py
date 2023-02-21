#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.version.semantic_version import semantic_version
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from ..attr.bfile_attr_value import bfile_attr_value

from .bfile_metadata_encoding import bfile_metadata_encoding
from .bfile_metadata_error import bfile_metadata_error
from .bfile_metadata_key import bfile_metadata_key

class bfile_metadata_handler(namedtuple('bfile_metadata_handler', 'key, getter, decoder, encoder, checker, old_keys')):

  def __new__(clazz, key, getter, decoder, encoder, checker, old_keys):
    key = check.check_bfile_metadata_key(key)
    check.check_callable(getter)
    check.check_callable(decoder)
    check.check_callable(encoder)
    check.check_callable(checker)
    check.check_string_seq(old_keys, allow_none = True)

    return clazz.__bases__[0].__new__(clazz, key, getter, decoder, encoder, checker, old_keys)

  @cached_property
  def attr_value(self):
    return bfile_attr_value(self.key.as_string, self.decoder, self.encoder, self.checker)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def get(self, filename):
    return self.getter(filename)

  def decode(self, value):
    return self.decoder(value)

  def encode(self, value):
    return self.encoder(value)
  
  def get_and_decode(self, filename):
    return self.decoder(self.get(filename))

  def check(self, value):
    return self.checker(value)
  
check.register_class(bfile_metadata_handler, include_seq = False, cast_func = bfile_metadata_handler._check_cast_func)
