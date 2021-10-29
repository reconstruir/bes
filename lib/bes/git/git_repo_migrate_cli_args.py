#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.common.check import check
from bes.git.git_repo_migrate_options import git_repo_migrate_options
from bes.git.git_clone_options import git_clone_options

from .git_cli_handler import git_cli_handler

class git_repo_migrate_cli_args(object):

  def __init__(self):
    pass
  
  def git_repo_migrate_add_args(self, subparser):
    # migrate
    p = subparser.add_parser('migrate', help = 'Migrate a repo from one remote to another.')
    p.add_argument('old_address', action = 'store', type = str, default = None,
                   help = 'The old remote address. [ None ]')
    p.add_argument('new_address', action = 'store', type = str, default = None,
                   help = 'The new remote address. [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   help = 'Verbose output.  Mostly for the results (git status and diff). [ False ]')
    p.add_argument('--debug', action = 'store_true',
                   help = 'Debug mode.  Print out the tmp dirs and do not delete them. [ False ]')
    p.add_argument('--lfs', action = 'store_true', default = False,
                   help = 'Migrate lfs objects as well. [ False ]')

  def _command_git_repo_migrate(self, command, *args, **kargs):
    from .git_repo_migrate_cli_handler import git_repo_migrate_cli_handler
    return git_repo_migrate_cli_handler(kargs).handle_command(command)
  
