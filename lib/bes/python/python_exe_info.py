#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..common.tuple_util import tuple_util
from ..version.semantic_version import semantic_version
from ..property.cached_property import cached_property

from .python_version import python_version
from .python_error import python_error

class python_exe_info(namedtuple('python_exe_info', 'exe, full_version, source, sys_executable, real_executable, exe_links, pip_exe')):

  def __new__(clazz, exe, full_version, source, sys_executable, real_executable, exe_links, pip_exe):
    check.check_string(exe)
    check.check_python_version(full_version)
    check.check_string(source)
    check.check_string(sys_executable)
    check.check_string(real_executable)
    check.check_string_seq(exe_links)
    check.check_string_seq(pip_exe)

    if not full_version.is_full_version():
      raise python_error('Not a full_version: "{full_version}"')
    
    return clazz.__bases__[0].__new__(clazz, exe, full_version, source, sys_executable, real_executable, exe_links, pip_exe)

  @cached_property
  def version(self):
    return self.full_version.version

  @cached_property
  def major_version(self):
    return self.full_version.major_version
  
check.register_class(python_exe_info, include_seq = False)
