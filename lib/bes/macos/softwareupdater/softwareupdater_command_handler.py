#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.system.check import check

from .softwareupdater import softwareupdater
from .softwareupdater_options import softwareupdater_options

from bes.macos.command_line_tools.command_line_tools_force import command_line_tools_force

class softwareupdater_command_handler(bcli_command_handler):

  def name(self):
    return 'softwareupdater'

  def _make_softwareupdater(self, options):
    return softwareupdater(softwareupdater_options(verbose=options.verbose,
                                                   sudo_password=options.sudo_password))

  def _command_available(self, force_command_line_tools, options):
    with command_line_tools_force(force=force_command_line_tools) as force:
      items = self._make_softwareupdater(options).available()
      for item in items:
        print('{} - {} - {}'.format(item.label, item.version, item.size))
    return 0

  def _command_install(self, label, options):
    check.check_string(label)

    self._make_softwareupdater(options).install(label, options.verbose)
    return 0
