#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.common.check import check

from .git_cli_common_options import git_cli_common_options

class git_cli_options(git_cli_common_options):

  def __init__(self, **kargs):
    super(git_cli_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'root_dir': os.getcwd(),
    })
  
  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(git_cli_options, self).check_value_types()
    check.check_string(self.root_dir)
    
check.register_class(git_cli_options)
