#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .git_clone_options import git_clone_options
from .git_cli_common_options import git_cli_common_options

class git_repo_cli_options(git_cli_common_options, git_clone_options):
  
  def __init__(self, *args, **kargs):
    git_cli_common_options.__init__(self, *args, **kargs)
    git_clone_options.__init__(self, *args, **kargs)
    self.address = None
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_string(self.address, allow_none = True)

check.register_class(git_repo_cli_options)
