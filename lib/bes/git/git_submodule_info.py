#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import re

from bes.common.check import check
from bes.common.string_util import string_util

class git_submodule_info(namedtuple('git_submodule_info', 'name, revision, is_current, tag')):

  def __new__(clazz, name, revision, is_current, tag):
    check.check_string(name)
    check.check_string(revision)
    check.check_bool(is_current)
    check.check_string(tag, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, name, revision, is_current, tag)

  @classmethod
  def parse(clazz, text):
    if text[0] == '-':
      is_current = False
      text_without_dash = text[1:].strip()      
    else:
      is_current = True
      text_without_dash = text.strip()      
    parts = string_util.split_by_white_space(text_without_dash, strip = True)
    if len(parts) < 2:
      raise ValueError('Invalid git submodule status: "{}"'.format(text_without_dash))
    revision = parts.pop(0)
    if len(revision) != 40:
      raise ValueError('Invalid git submodule revision: "{}"'.format(revision))
    name = parts.pop(0)
    if len(parts) > 0:
      tag = clazz._parse_tag(parts.pop(0))
    else:
      tag = None
    return git_submodule_info(name, revision, is_current, tag)

  @classmethod
  def _parse_tag(clazz, s):
    f = re.findall('\((.+)\)', s)
    if not f or not len(f) == 1:
      raise ValueError('Invalid git submodule tag: "{}"'.format(s))
    return f[0]
  
check.register_class(git_submodule_info)
  
