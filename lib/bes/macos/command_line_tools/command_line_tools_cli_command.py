#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.macos.softwareupdater.softwareupdater import softwareupdater

from .command_line_tools import command_line_tools

class command_line_tools_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(command_line_tools_cli_command, command)
    return func(**kargs)
  
  @classmethod
  def installed(clazz):
    if command_line_tools.installed():
      return 0
    return 1

  @classmethod
  def install(clazz):
    available = softwareupdater.available(force_command_line_tools = True)
    print(available)
    return 0
  
  @classmethod
  def ensure(clazz):
    if clazz.installed():
      return 0
    return clazz.install()
  
