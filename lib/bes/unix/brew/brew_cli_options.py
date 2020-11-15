#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.dict_util import dict_util

class brew_cli_options(object):
  
  def __init__(self, *args, **kargs):
    self.verbose = False
    self.password = None
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_string(self.password, allow_none = True)

  def __str__(self):
    return str(dict_util.hide_passwords(self.__dict__, [ 'password' ]))

check.register_class(brew_cli_options)
