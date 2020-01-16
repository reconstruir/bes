#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .git_clone_options import git_clone_options

class git_repo_operation_options(git_clone_options):
  
  def __init__(self, *args, **kargs):
    super(git_repo_operation_options, self).__init__(*args, **kargs)
    self.dry_run = False
    self.debug = False
    self.verbose = False
    self.num_tries = 10
    self.retry_wait_ms = 0.500
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.dry_run)
    check.check_bool(self.debug)
    check.check_bool(self.verbose)
    check.check_int(self.num_tries)
    check.check_float(self.retry_wait_ms)

check.register_class(git_repo_operation_options)
