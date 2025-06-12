#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from os import path

from collections import namedtuple

from ..system.check import check
from bes.property.cached_property import cached_property

class dim_task_result(namedtuple('dim_task_result', 'success, log, descriptor')):

  def __new__(clazz, success, log, descriptor):
    check.check_bool(success)
    check.check_string(log)
    check.check_dim_task_descriptor(descriptor)
    
    return clazz.__bases__[0].__new__(clazz, success, log, descriptor)

  @cached_property
  def log_relative(self):
    return path.relpath(self.log)

  @cached_property
  def bat_docker_tag(self):
    return self.descriptor.bat_docker_tag
  
check.register_class(dim_task_result)
