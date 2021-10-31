#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.dict_util import dict_util

from .git_clone_options import git_clone_options
from .git_cli_common_options import git_cli_common_options

class git_repo_cli_options(git_cli_common_options, git_clone_options):

  def __init__(self, *args, **kargs):
    git_cli_common_options.__init__(self, *args, **kargs)
    git_clone_options.__init__(self, *args, **kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    d1 = git_cli_common_options.default_values()
    d2 = git_clone_options.default_values()
    d3 = {
      'address': None,
    }
    return dict_util.combine(d1, d2, d3)

  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    'Return a dict of defaults for these options.'
    d1 = git_cli_common_options.value_type_hints()
    d2 = git_clone_options.value_type_hints()
    d3 = {}
    return dict_util.combine(d1, d2, d3)
  
  
  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    git_cli_common_options.check_value_types(self)
    git_clone_options.check_value_types(self)

    check.check_string(self.address, allow_none = True)
    
check.register_class(git_repo_cli_options)
