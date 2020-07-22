#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
from bes.common.check import check

class git_clone_options(object):
  
  def __init__(self, *args, **kargs):
    self.enforce_empty_dir = True
    self.depth = None
    self.lfs = False
    self.jobs = None
    self.submodules = False
    self.submodules_recursive = False
    self.submodule_list = None
    self.branch = None
    self.reset_to_head = False
    self.clean = False
    self.clean_immaculate = False
    self.no_network = False
    self.num_tries = 1
    self.retry_wait_seconds = 10.0
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.enforce_empty_dir)
    check.check_int(self.depth, allow_none = True)
    check.check_bool(self.lfs)
    check.check_int(self.jobs, allow_none = True)
    check.check_bool(self.submodules)
    check.check_bool(self.submodules_recursive)
    check.check_list(self.submodule_list, allow_none = True)
    check.check_string(self.branch, allow_none = True)
    check.check_bool(self.reset_to_head)
    check.check_bool(self.no_network)
    check.check_bool(self.clean)
    check.check_bool(self.clean_immaculate)
    check.check_int(self.num_tries)
    check.check_float(self.retry_wait_seconds)

  def __str__(self):
    return str(self.__dict__)

  def pformat(self):
    return pprint.pformat(self.__dict__)
  
check.register_class(git_clone_options)
