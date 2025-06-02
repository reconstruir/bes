#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.version.semantic_version import semantic_version
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from .bf_metadata_error import bf_metadata_error

class bf_metadata_key(namedtuple('bf_metadata_key', 'domain, group, name, version')):

  DELIMITER = '__'
  
  def __new__(clazz, domain, group, name, version):
    clazz.check_part(domain)
    clazz.check_part(group)
    clazz.check_part(name)
    version = check.check_semantic_version(version)

    return clazz.__bases__[0].__new__(clazz, domain, group, name, version)

  def __hash__(self):
    return hash(self.as_string)
  
  def __str__(self):
    return self.as_string

  @cached_property
  def as_string(self):
    return self.DELIMITER.join([ self.domain, self.group, self.name, str(self.version) ])

  @classmethod
  def check_part(clazz, part):
    check.check_string(part)

    for c in ( ' ', ':', clazz.DELIMITER ):
      if c in part:
        if c == ' ':
          label = 'space'
        else:
          label = c
        raise bf_metadata_error(f'"{label}" not supported in part: "{part}"')
    return part
  
  @classmethod
  def parse_key(clazz, s):
    check.check_string(s)

    parts = s.split(clazz.DELIMITER)
    if len(parts) != 4:
      raise bf_metadata_error(f'Invalid number of parts {len(parts)} instead of 4: "{s}"')
    return bf_metadata_key(*parts)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    if check.is_string(obj):
      return clazz.parse_key(obj)
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(bf_metadata_key, include_seq = False, cast_func = bf_metadata_key._check_cast_func)
