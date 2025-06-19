#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod
from abc import ABC

from ..system.check import check
from ..system.log import logger

class bcli_parser_maker_i(ABC):

  _log = logger('bcli')
  
  @classmethod
  @abstractmethod
  def make_parser(clazz):
    raise NotImplementedError(f'make_parser')

check.register_class(bcli_parser_maker_i, name = 'bcli_parser_maker', include_seq = False)
