#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.common.string_util import string_util

class file_mode(object):
  'Deal with file mode permissions.'

  @classmethod
  def parse_mode(clazz, m):
    if string_util.is_string(m):
      return int(m, 8)
    if isinstance(m, int):
      return m
    return None
