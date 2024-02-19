#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from ..system.check import check

from .btl_lexer_options import btl_lexer_options

class btl_parser_options(object):

  def __init__(self, *args, **kargs):
    self.verbose = False
    self.lexer_options = btl_lexer_options()
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)
    check.check_btl_lexer_options(self.lexer_options)

  def __str__(self):
    return pprint.pformat(self.__dict__)
  
check.register_class(btl_parser_options, include_seq = False)
