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
    
  MACOS_COMMAND_GROUPS = []
  if host.is_macos():
    from bes.macos.command_line_tools.command_line_tools_cli_args import command_line_tools_cli_args
    from bes.macos.defaults.defaults_cli_args import defaults_cli_args
    from bes.macos.scutil.scutil_cli_args import scutil_cli_args
    from bes.macos.softwareupdater.softwareupdater_cli_args import softwareupdater_cli_args
    MACOS_COMMAND_GROUPS = [
      cli_command('command_line_tools', 'command_line_tools_add_args', 'Deal with command line tools', command_line_tools_cli_args),
      cli_command('defaults', 'defaults_add_args', 'Deal with defaults', defaults_cli_args),
      cli_command('scutil', 'scutil_add_args', 'Deal with scutil', scutil_cli_args),
      cli_command('softwareupdater', 'softwareupdater_add_args', 'Deal with macos softwareupdate', softwareupdater_cli_args),
    ]

  UNIX_COMMAND_GROUPS = []
  if host.is_unix():
    from bes.unix.brew.brew_cli_args import brew_cli_args
    from bes.unix.brew_installer.brew_installer_cli_args import brew_installer_cli_args
    from bes.unix.shell.shell_cli_args import shell_cli_args
    from bes.unix.sudo.sudo_cli_args import sudo_cli_args
    UNIX_COMMAND_GROUPS = [
      cli_command('brew', 'brew_add_args', 'Deal with brew', brew_cli_args),
      cli_command('brew_installer', 'brew_installer_add_args', 'Deal with brew install', brew_installer_cli_args),
      cli_command('shell', 'shell_add_args', 'Deal with shell', shell_cli_args),
      cli_command('sudo', 'sudo_add_args', 'Deal with sudo', sudo_cli_args),
    ]
    
  from bes.archive.archive_cli_args import archive_cli_args
  from bes.computer_setup.computer_setup_cli_args import computer_setup_cli_args
  from bes.egg.egg_cli_args import egg_cli_args
  from bes.git.git_cli_args import git_cli_args
  from bes.git.git_identity_cli_args import git_identity_cli_args
  from bes.git.git_repo_cli_args import git_repo_cli_args
  from bes.git.git_repo_document_cli_args import git_repo_document_cli_args
  from bes.git.git_repo_script_cli_args import git_repo_script_cli_args
  from bes.native_package.native_package_cli_args import native_package_cli_args
  from bes.pip.pip_cli_args import pip_cli_args
  from bes.python.python_cli_args import python_cli_args
  from bes.python.python_installer_cli_args import python_installer_cli_args
  COMMON_COMMAND_GROUPS = [
    cli_command('archive', 'archive_add_args', 'Deal with archive', archive_cli_args),
    cli_command('computer_setup', 'computer_setup_add_args', 'Deal with computer setup', computer_setup_cli_args),
    cli_command('egg', 'egg_add_args', 'Deal with eggs', egg_cli_args),
    cli_command('git', 'git_add_args', 'Deal with git', git_cli_args),
    cli_command('git_identity', 'git_identity_add_args', 'Deal with git identity', git_identity_cli_args),
    cli_command('git_repo', 'git_repo_add_args', 'Deal with git repos', git_repo_cli_args),
    cli_command('git_repo_script', 'git_repo_script_add_args', 'Deal with git repo scipts', git_repo_script_cli_args),
    cli_command('git_repo_document', 'git_repo_document_add_args', 'Deal with git documents', git_repo_document_cli_args),
    cli_command('native_package', 'native_package_add_args', 'Deal with native packages', native_package_cli_args),
    cli_command('pip', 'pip_add_args', 'Pip stuff', pip_cli_args),
    cli_command('python', 'python_add_args', 'Deal with python', python_cli_args),
    cli_command('python_installer', 'python_installer_add_args', 'Deal with python install', python_installer_cli_args),
  ]

  COMMAND_GROUPS = COMMON_COMMAND_GROUPS + MACOS_COMMAND_GROUPS + UNIX_COMMAND_GROUPS
  
  #@abstractmethod
  def command_group_list(self):
    'Return a list of command groups for this cli.'
    return self.COMMAND_GROUPS

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
