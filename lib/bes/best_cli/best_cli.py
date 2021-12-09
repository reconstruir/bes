# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys, warnings

# So for Python 2.7 we supress CryptographyDeprecationWarning warnings
if sys.version_info.major == 2 and sys.version_info.minor == 7:
  warnings.filterwarnings(action = 'ignore', module = 'OpenSSL')

from bes.cli.cli import cli
from bes.cli.cli_command import cli_command

class best_cli(cli):

  def __init__(self):
    super(best_cli, self).__init__('best')
    
  from bes.system.host import host

  _command_groups = []

  if host.is_macos():
    from .best_cli_macos import MACOS_COMMAND_GROUPS
    _command_groups.extend(MACOS_COMMAND_GROUPS)

  if host.is_unix():
    from .best_cli_unix import UNIX_COMMAND_GROUPS
    _command_groups.extend(UNIX_COMMAND_GROUPS)
    
  if host.is_windows():
    from .best_cli_windows import WINDOWS_COMMAND_GROUPS
    _command_groups.extend(WINDOWS_COMMAND_GROUPS)
    
  from .best_cli_common import COMMON_COMMAND_GROUPS
  _command_groups.extend(COMMON_COMMAND_GROUPS)
  
  #@abstractmethod
  def command_group_list(self):
    'Return a list of command groups for this cli.'
    return self._command_groups

  from bes.cli.cli_env_cli_args import cli_env_cli_args
  from bes.cli.cli_version_cli_args import cli_version_cli_args
  from bes.cli.cli_help_cli_args import cli_help_cli_args
  cli_version_cli_args.version_module_name = 'bes'
  cli_version_cli_args.version_dependencies = None
  COMMANDS = [
    cli_command('env', 'env_add_args', 'Print env information', cli_env_cli_args),
    cli_command('help', 'help_add_args', 'Print help', cli_help_cli_args),
    cli_command('version', 'version_add_args', 'Print version information', cli_version_cli_args),
  ]
  
  #@abstractmethod
  def command_list(self):
    'Return a list of commands for this cli.'
    return self.COMMANDS
  
  @classmethod
  def run(clazz):
    raise SystemExit(best_cli().main())
