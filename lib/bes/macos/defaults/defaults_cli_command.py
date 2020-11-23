#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

from .defaults import defaults

from bes.macos.command_line_tools.command_line_tools_force import command_line_tools_force

class defaults_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(defaults_cli_command, command)
    return func(**kargs)
  
  @classmethod
  def read_domain(clazz, domain, style):
    check.check_string(domain)
    check.check_string(style)

    s = defaults.read_domain(domain, style)
    print(s)
    return 0
