#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from ..system.check import check
from bes.property.cached_property import cached_property

import pprint

class dim_task_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.follow = False
    self.log = False
    self.more_args = []
    self.test = False
    self.build = False
    self.publish_egoist = False
    self.publish_image = False
    self.no_pull = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_bool(self.follow)
    check.check_bool(self.log)
    check.check_string_seq(self.more_args)
    check.check_bool(self.test)
    check.check_bool(self.build)
    check.check_bool(self.publish_egoist)
    check.check_bool(self.publish_image)
    check.check_bool(self.no_pull)

  def __str__(self):
    return str(self.__dict__)

  def pformat(self):
    return pprint.pformat(self.__dict__)

  @cached_property
  def script_args(self):
    result = []
    if self.verbose:
      result.append('verbose=true')
    if self.test:
      result.append('test=true')
    if self.build:
      result.append('build=true')
    if self.publish_egoist:
      result.append('publish_egoist=true')
    if self.publish_image:
      result.append('publish_image=true')
    if self.follow:
      result.append('follow=true')
    if self.no_pull:
      result.append('no_pull=true')
    result.extend(self.more_args)
    return result
  
check.register_class(dim_task_options)
