#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..system.log import logger
from ..property.cached_property import cached_property

from .bcli_command_factory_i import bcli_command_factory_i

class bcli_command_factory_base(bcli_command_factory_i):

  _log = logger('bcli')

  @cached_property
  def default_options_instance(self):
    options_class = self.options_class()
    return options_class()

  def default(self, name):
    check.check_string(name)

    return self.default_options_instance.desc.default(name)
  
check.register_class(bcli_command_factory_base, name = 'bcli_parser_factory', include_seq = False)
