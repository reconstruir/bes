#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod
from bes.common.object_util import object_util

class matcher_base(object):
  'Abstract base class for matcher.'

  def __init__(self):
    pass

  @abstractmethod
  def match(self, text):
    pass

  def filter(self, texts, negate = False):
    texts = object_util.listify(texts)
    result = []
    for text in texts:
      matches = self.match(text)
      if negate:
        matches = not matches
      if matches:
        result.append(text)
    return result

  @staticmethod
  def _match_any(match_func, filename, patterns):
    for pattern in patterns:
      if match_func(filename, pattern):
        return True
    return False

  @staticmethod
  def _match_all(match_func, filename, patterns):
    for pattern in patterns:
      if not match_func(filename, pattern):
        return False
    return True

  @staticmethod
  def _match_none(match_func, filename, patterns):
    for pattern in patterns:
      if match_func(filename, pattern):
        return False
    return True
