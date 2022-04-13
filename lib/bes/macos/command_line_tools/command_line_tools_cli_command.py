#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check

from .command_line_tools import command_line_tools

class command_line_tools_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(command_line_tools_cli_command, command)
    return func(**kargs)
  
  @classmethod
  def installed(clazz, verbose):
    if command_line_tools.installed(verbose):
      return 0
    return 1

  @classmethod
  def install(clazz, verbose):
    command_line_tools.install(verbose)
    return 0
  
  @classmethod
  def ensure(clazz, verbose):
    command_line_tools.ensure(verbose)
    return 0
