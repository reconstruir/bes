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
  def get_domain(clazz, domain, style):
    check.check_string(domain)
    check.check_string(style)

    s = defaults.get_domain(domain, style)
    print(s)
    return 0

  @classmethod
  def get_value(clazz, domain, key):
    check.check_string(domain)
    check.check_string(key)

    s = defaults.get_value(domain, key)
    print(s)
    return 0

  @classmethod
  def set_value(clazz, domain, key, value):
    check.check_string(domain)
    check.check_string(key)
    check.check_string(value)

    defaults.set_value(domain, key, value)
    return 0
  
