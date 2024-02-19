#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import pprint

from ..system.check import check
from ..property.cached_property import cached_property

from .btl_lexer_options import btl_lexer_options

class btl_parser_options(object):

  def __init__(self, *args, **kargs):
    self.source = '<unknown>'
    self.verbose = False
    self.variables = {}
    for key, value in kargs.items():
      setattr(self, key, value)
    check.check_bool(self.verbose)

  def __str__(self):
    return pprint.pformat(self.__dict__)

  @cached_property
  def lexer_options(self):
    return btl_lexer_options(source = self.source,
                             variables = self.variables,
                             verbose = self.verbose)
  
check.register_class(btl_parser_options, include_seq = False)
