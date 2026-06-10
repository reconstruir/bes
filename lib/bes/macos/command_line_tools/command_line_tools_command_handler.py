#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler

from .command_line_tools import command_line_tools

class command_line_tools_command_handler(bcli_command_handler):

  def name(self):
    return 'command_line_tools'

  def _command_installed(self, options):
    if command_line_tools.installed(options.verbose):
      return 0
    return 1

  def _command_install(self, options):
    command_line_tools.install(options.verbose)
    return 0

  def _command_ensure(self, options):
    command_line_tools.ensure(options.verbose)
    return 0
