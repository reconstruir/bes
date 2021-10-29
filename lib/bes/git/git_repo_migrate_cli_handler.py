#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.cli.cli_command_handler import cli_command_handler
from bes.system.command_line import command_line

from .git_repo_migrate_options import git_repo_migrate_options
from .git_repo_migrate import git_repo_migrate

class git_repo_migrate_cli_handler(cli_command_handler):

  def __init__(self, cli_args):
    super(git_repo_migrate_cli_handler, self).__init__(cli_args, options_class = git_repo_migrate_options)
    check.check_git_repo_migrate_options(self.options)
  
  def migrate(self, old_address, new_address):
    check.check_string(old_address)
    check.check_string(new_address)

    git_repo_migrate.migrate(old_address, new_address, options = self.options)
    return 0
