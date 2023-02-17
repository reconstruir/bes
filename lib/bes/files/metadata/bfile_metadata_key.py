#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check
from bes.version.semantic_version import semantic_version
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property

from .bfile_metadata_error import bfile_metadata_error

class bfile_metadata_key(namedtuple('bfile_metadata_key', 'domain, group, name, version')):

  DELIMITER = '/'
  
  def __new__(clazz, domain, group, name, version):
    clazz.check_part(domain)
    clazz.check_part(group)
    clazz.check_part(name)
    version = check.check_semantic_version(version)

    return clazz.__bases__[0].__new__(clazz, domain, group, name, version)

  def __hash__(self):
    return hash(self._as_str)
  
  def __str__(self):
    return self._as_str

  @cached_property
  def _as_str(self):
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
        raise bfile_metadata_error(f'"{label}" not supported in part: "{part}"')
    return part
  
  @classmethod
  def parse_key(clazz, s):
    check.check_string(s)

    parts = s.split(clazz.DELIMITER)
    if len(parts) != 4:
      raise bfile_metadata_error(f'Invalid number of parts {len(parts)} instead of 4: "{s}"')
    return bfile_metadata_key(*parts)
  
  @classmethod
  def _check_cast_func(clazz, obj):
    if check.is_string(obj):
      return clazz.parse_key(obj)
    return tuple_util.cast_seq_to_namedtuple(clazz, obj)
  
check.register_class(bfile_metadata_key, include_seq = False, cast_func = bfile_metadata_key._check_cast_func)
