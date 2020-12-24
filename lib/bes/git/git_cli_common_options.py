#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint
from bes.common.check import check

class git_cli_common_options(object):
  
  def __init__(self, *args, **kargs):
    self.debug = False
    self.dry_run = False
    self.output_style = 'table'
    self.output_filename = None
    self.verbose = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.debug)
    check.check_bool(self.dry_run)
    check.check_string(self.output_style)
    check.check_string(self.output_filename, allow_none = True)
    assert self.output_style in [ 'brief', 'table', 'json', 'plain' ]
    check.check_bool(self.verbose)

  def __str__(self):
    return str(self.__dict__)

  def pformat(self):
    return pprint.pformat(self.__dict__)
  
check.register_class(git_cli_common_options)
