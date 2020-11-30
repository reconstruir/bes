# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys

class cli_help_cli_args(object):

  parser = None
  
  def help_add_args(self, parser):
    pass
  
  def _command_help(self, command, *args, **kargs):
    assert command == None
    assert self.parser != None
    self.parser.print_help()
    return 0
