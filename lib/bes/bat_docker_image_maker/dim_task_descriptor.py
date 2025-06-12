#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from collections import namedtuple

from ..system.check import check
from bes.property.cached_property import cached_property

class dim_task_descriptor(namedtuple('dim_task_descriptor', 'function, step_name, system, python_version, options')):

  def __new__(clazz, function, step_name, system, python_version, options):
    check.check_string(step_name)
    check.check_string(system)
    check.check_string(python_version)
    check.check_dim_task_options(options)
    
    return clazz.__bases__[0].__new__(clazz, function, step_name, system, python_version, options)
  
  @cached_property
  def bat_docker_tag(self):
    return 'ego_cicd_{}-py{}-{}'.format(self.step_name, self.python_version, self.system)

  def log_filename(self):
    return '{}.log'.format(self.bat_docker_tag)

  @cached_property
  def script_args(self):
    result = [
      'python_version={}'.format(self.python_version),
    ]
    result.extend(self.options.script_args)
    return result
      
check.register_class(dim_task_descriptor)
