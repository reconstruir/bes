#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, pprint
from bes.common.check import check

class git_cli_options(object):
  
  def __init__(self, *args, **kargs):
    cwd = os.getcwd()
    self.root_dir = cwd
    for key, value in kargs.items():
      setattr(self, key, value)
    self.root_dir = self.root_dir or cwd
    check.check_string(self.root_dir, allow_none = True)

  def __str__(self):
    return str(self.__dict__)

  def pformat(self):
    return pprint.pformat(self.__dict__)
  
check.register_class(git_cli_options)
