#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.log import logger
from ..system.check import check

from .hconfig_error import hconfig_error

class hconfig_path(object):

  def __init__(self, path, wildcards = False):
    check.check_string(path)
    check.check_bool(wildcards)

    self._path = path
    self._wildcards = wildcards
    self.parts = self._parse_parts(path, self._wildcards)

  def __getitem__(self, i):
    return self.parts[i]
    
  @classmethod
  def _parse_parts(clazz, s, wildcards):
    parts = s.split('.')
    for part in parts:
      if not clazz._path_part_is_valid(part, wildcards):
        raise hconfig_error(f'Invalid path path "{part}": {path}')
    return parts

  _WILDCARD_CHARS = ( '?', '*', '[', ']', '!', '-' )
  @classmethod
  def _part_first_char_is_valid(clazz, c, wildcards):
    if wildcards and c in clazz._WILDCARD_CHARS:
      return True
    return c.isalpha() or c == '_'

  @classmethod
  def _part_next_char_is_valid(clazz, c, wildcards):
    if wildcards and c in clazz._WILDCARD_CHARS:
      return True
    return c.isalnum() or c == '_'
  
  @classmethod
  def _path_part_is_valid(clazz, part, wildcards):
    if not part:
      return False
    if not clazz._part_first_char_is_valid(part[0], wildcards):
      return False
    for c in part[1:]:
      if not clazz._part_next_char_is_valid(c, wildcards):
        return False
    return True
