# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import abc

class bcli_application_i(abc.ABC):
  
  @abc.abstractmethod
  def name(self):
    raise NotImplementedError(f'name')
      
  @abc.abstractmethod
  def parser_factories(self):
    raise NotImplementedError(f'parser_factories')
