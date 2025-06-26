# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod
from abc import ABC

from ..system.check import check
from ..system.log import logger

class bcli_application_i(ABC):

  _log = logger('bcli')
  
  @abstractmethod
  def name(self):
    raise NotImplementedError(f'name')
      
  @abstractmethod
  def parser_factories(self):
    raise NotImplementedError(f'parser_factories')
