#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

from .software_updater import software_updater

class software_updater_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(software_updater_cli_command, command)
    return func(**kargs)
  
  @classmethod
  def available(clazz, force_command_line_tools):
    check.check_bool(force_command_line_tools)

    items = software_updater.available(force_command_line_tools)
    for item in items:
      print('{} - {} - {}'.format(item.label, item.version, item.size))
    return 0
