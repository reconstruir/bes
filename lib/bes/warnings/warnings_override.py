#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
import warnings

from bes.system.check import check

class warnings_override(object):

  def __init__(self, major_version, minor_version, action = None, category = None):
    check.check_int(major_version)
    check.check_int(minor_version, allow_none = True)
    check.check_string(action, allow_none = True)
    check.check_class(category, allow_none = True)
    
    self._major_version = major_version
    self._minor_version = minor_version
    self._action = action
    self._category = category
    
  def __enter__(self):
    if self._python_version_matches(self._major_version, self._minor_version):
      warnings.filterwarnings(self._action, category = self._category)
    return self
  
  def __exit__(self, type, value, traceback):
    if self._python_version_matches(self._major_version, self._minor_version):
      warnings.resetwarnings()

  @classmethod
  def _python_version_matches(clazz, major_version, minor_version):
    if major_version != sys.version_info.major:
      return False
    if minor_version != None:
      return sys.version_info.minor >= minor_version
    return True
