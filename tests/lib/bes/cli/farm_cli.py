#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli import cli
from bes.cli.cli_command import cli_command

class farm_cli(cli):

  def __init__(self):
    super(farm_cli, self).__init__('farm')
    
  #@abstractmethod
  def command_group_list(self):
    'Return a list of command groups for this cli.'
    from fruit_cli_args import fruit_cli_args
    from cheese_cli_args import cheese_cli_args
    return [
      cli_command('fruit', 'fruit_add_args', 'Deal with fruit', fruit_cli_args),
      cli_command('cheese', 'cheese_add_args', 'Deal with cheese', cheese_cli_args),
    ]

  #@abstractmethod
  def command_list(self):
    'Return a list of commands for this cli.'
    from bes.cli.cli_env_cli_args import cli_env_cli_args
    from bes.cli.cli_version_cli_args import cli_version_cli_args
    from bes.cli.cli_help_cli_args import cli_help_cli_args
    cli_version_cli_args.version_module_name = 'bes'
    cli_version_cli_args.version_dependencies = None
    return [
      cli_command('env', 'env_add_args', 'Print env information', cli_env_cli_args),
      cli_command('help', 'help_add_args', 'Print help', cli_help_cli_args),
      cli_command('version', 'version_add_args', 'Print version information', cli_version_cli_args),
    ]
  
  @classmethod
  def run(clazz):
    raise SystemExit(farm_cli().main())
