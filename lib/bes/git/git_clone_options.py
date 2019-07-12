#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

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
check.register_class(git_clone_options)
