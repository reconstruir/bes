#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from ..system.check import check

class btl_lexer_options(object):

  def __init__(self, *args, **kargs):
    self.source = None
    self.verbose = False
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_string(self.source, allow_none = True)
    check.check_bool(self.verbose)

  def __str__(self):
    return pprint.pformat(self.__dict__)
  
check.register_class(btl_lexer_options, include_seq = False)
