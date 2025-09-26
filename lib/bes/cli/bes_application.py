#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.bcli.bcli_application import bcli_application

from ..files.duplicates.bf_file_dups_command_factory import bf_file_dups_command_factory
from ..files.resolve.bf_file_resolver_command_factory import bf_file_resolver_command_factory

class bes_application(bcli_application):

  #@abstractmethod
  def name(self):
    return 'bes'
  
  #@abstractmethod
  def parser_factories(self):
    return [
      bf_file_dups_command_factory,
      bf_file_resolver_command_factory,
    ]
