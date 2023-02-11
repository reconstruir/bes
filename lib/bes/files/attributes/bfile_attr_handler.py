#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.version.semantic_version import semantic_version
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from .bfile_attr_decode import bfile_attr_decode

class bfile_attr_handler(namedtuple('bfile_attr_handler', 'domain, key, version, getter, decoder, memory_only')):

  def __new__(clazz, domain, key, version, getter, decoder, memory_only):
    check.check_string(domain)
    check.check_string(key)
    version = check.check_semantic_version(version)
    check.check_callable(getter)
    check.check_callable(decoder)
    check.check_bool(memory_only)

    return clazz.__bases__[0].__new__(clazz, domain, key, version, getter, decoder, memory_only)

  @cached_property
  def factory_key(self):
    return self.make_factory_key(self.domain, self.key, self.version)

  @classmethod
  def make_factory_key(clazz, domain, key, version):
    return f'{domain}.{key}.{version}'
  
  @classmethod
  def _check_cast_func(clazz, obj):
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
  def get(self, filename):
    return self._getter(filename)

  def decode(self, value):
    return self._decoder(value)

check.register_class(bfile_attr_handler, include_seq = False, cast_func = bfile_attr_handler._check_cast_func)
