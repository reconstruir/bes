#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..script.blurb import blurb
from ..system.check import check
from ..system.log import log
from ..system.log import logger

from .bcli_command_handler_i import bcli_command_handler_i

class bcli_command_handler(bcli_command_handler_i):

  _log = logger('bcli')
  
  def __init__(self):
    name = self.name()
    check.check_string(name)

    blurb.add_blurb(self, name)
    log.add_logging(self, name)
    
  def handle_boolean_result(self, result, verbose):
    check.check_bool(result)
    
    if verbose:
      print(str(result))
    return 0 if result else 1
