#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, pprint
from bes.common.check import check

from .git_cli_common_options import git_cli_common_options

class git_cli_options(git_cli_common_options):
  
  def __init__(self, *args, **kargs):
    self.root_dir = None
    for key, value in kargs.items():
      setattr(self, key, value)
    self.root_dir = self.root_dir or os.getcwd()
    check.check_string(self.root_dir, allow_none = True)

check.register_class(git_cli_options)
