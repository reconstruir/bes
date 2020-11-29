#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

from .softwareupdater import softwareupdater

from bes.macos.command_line_tools.command_line_tools_force import command_line_tools_force

class softwareupdater_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(softwareupdater_cli_command, command)
    return func(**kargs)
  
  @classmethod
  def available(clazz, force_command_line_tools):
    with command_line_tools_force(force = force_command_line_tools) as force:
      items = softwareupdater.available()
      for item in items:
        print('{} - {} - {}'.format(item.label, item.version, item.size))
      return 0

  @classmethod
  def install(clazz, label, verbose):
    check.check_string(label)

    softwareupdater.install(label, verbose)
    return 0
  
