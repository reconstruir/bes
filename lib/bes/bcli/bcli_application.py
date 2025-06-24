# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

from abc import abstractmethod
from abc import ABC

from ..system.check import check
from ..script.blurb import blurb
from ..system.log import log

from .bcli_parser_manager import bcli_parser_manager

class bcli_application(ABC):

  def __init__(self):
    name = self.name()
    check.check_string(name)

    log.add_logging(self, name)
    blurb.add_blurb(self, name)

    self._parser_manager = bcli_parser_manager()
    for next_parser_factory in self.parser_factories():
      self._parser_manager.register_factory(next_parser_factory)

  @abstractmethod
  def name(self):
    raise NotImplementedError(f'name')
      
  @abstractmethod
  def parser_factories(self):
    raise NotImplementedError(f'parser_factories')
    
  def run(self, args):
#    argv = sys.argv[1:]
#    args = ' '.join(argv)
    self.log_d(f'args="{args}"')
    ns = self._parser_manager.parse_args(args)
    self.log_d(f'ns={ns}')
