# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli import cli
from bes.cli.cli_item import cli_item

class best_cli(cli):

  def __init__(self):
    super(best_cli, self).__init__('best', 'bes', [])

  from bes.system.host import host
    
  MACOS_ITEMS = []
  if host.is_macos():
    from bes.macos.command_line_tools.command_line_tools_cli_args import command_line_tools_cli_args
    from bes.macos.defaults.defaults_cli_args import defaults_cli_args
    from bes.macos.softwareupdater.softwareupdater_cli_args import softwareupdater_cli_args
    MACOS_ITEMS = [
      cli_item('command_line_tools', 'command_line_tools_add_args', 'Deal with command line tools', command_line_tools_cli_args),
      cli_item('defaults', 'defaults_add_args', 'Deal with defaults', defaults_cli_args),
      cli_item('softwareupdater', 'softwareupdater_add_args', 'Deal with macos softwareupdate', softwareupdater_cli_args),
    ]

  UNIX_ITEMS = []
  if host.is_unix():
    from bes.unix.brew.brew_cli_args import brew_cli_args
    from bes.unix.brew_installer.brew_installer_cli_args import brew_installer_cli_args
    from bes.unix.shell.shell_cli_args import shell_cli_args
    from bes.unix.sudo.sudo_cli_args import sudo_cli_args
    UNIX_ITEMS = [
      cli_item('brew', 'brew_add_args', 'Deal with brew', brew_cli_args),
      cli_item('brew_installer', 'brew_installer_add_args', 'Deal with brew install', brew_installer_cli_args),
      cli_item('shell', 'shell_add_args', 'Deal with shell', shell_cli_args),
      cli_item('sudo', 'sudo_add_args', 'Deal with sudo', sudo_cli_args),
    ]
    
  from bes.archive.archive_cli_args import archive_cli_args
  from bes.computer_setup.computer_setup_cli_args import computer_setup_cli_args
  from bes.native_package.native_package_cli_args import native_package_cli_args
  from bes.egg.egg_cli_args import egg_cli_args
  COMMON_ITEMS = [
    cli_item('archive', 'archive_add_args', 'Deal with archive', archive_cli_args),
    cli_item('egg', 'egg_add_args', 'Deal with eggs', egg_cli_args),
    cli_item('computer_setup', 'computer_setup_add_args', 'Deal with computer setup', computer_setup_cli_args),
    cli_item('native_package', 'native_package_add_args', 'Deal with native packages', native_package_cli_args),
  ]

  ITEMS = COMMON_ITEMS + MACOS_ITEMS + UNIX_ITEMS
  
  #@abstractmethod
  def tool_item_list(self):
    'Return a list of tool items for this cli.'
    return self.ITEMS
  
  @classmethod
  def run(clazz):
    raise SystemExit(best_cli().main())
