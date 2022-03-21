#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
import warnings

from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.system.check import check
from bes.version.semantic_version import semantic_version

class warnings_override(object):

  def __init__(self, clauses = None, action = None, category = None, python_version = None):
    check.check_string(action, allow_none = True)
    check.check_string(python_version, allow_none = True)
    check.check_class(category, allow_none = True)

    python_version = semantic_version(python_version or self._python_system_version())

    self._matches = self._python_version_matches(python_version, clauses)
    self._clauses = clauses
    self._action = action
    self._category = category
    
  def __enter__(self):
    if self._matches:
      warnings.filterwarnings(self._action, category = self._category)
    return self
  
  def __exit__(self, type, value, traceback):
    if self._matches:
      warnings.resetwarnings()

  @classmethod
  def _python_version_matches(clazz, python_version, clauses):
    if not clauses:
      return True
    return python_version.match_clause(clauses)

  @classmethod
  def _python_system_version(clazz):
    info = sys.version_info
    return f'{info.major}.{info.minor}.{info.micro}'
