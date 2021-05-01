#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.common.check import check
from bes.git.git_repo_script_options import git_repo_script_options
from bes.git.git_clone_options import git_clone_options

from .git_cli_command import git_cli_command

class git_repo_script_cli_args(object):

  def __init__(self):
    pass
  
  def git_repo_script_add_args(self, subparser):
    # git_repo_run_scripts
    p = subparser.add_parser('repo_run_scripts', help = 'Clone a repo and run a script in it.')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('scripts', action = 'store', nargs = '*', default = None,
                   help = 'Scripts to run one per argument.  Use quotes to include args for the scripts. [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   help = 'Verbose output.  Mostly for the results (git status and diff). [ False ]')
    p.add_argument('--push', action = 'store_true',
                   help = 'Push to the origin when done. [ False ]')
    p.add_argument('--bump-tag', action = 'store', type = str, default = None,
                   dest = 'bump_tag_component',
                   help = 'Bump the repo tag when done. [ False ]')
    p.add_argument('--dry-run', action = 'store_true',
                   help = 'Dont do it just print it. [ False ]')
    p.add_argument('--debug', action = 'store_true',
                   help = 'Debug mode.  Print out the tmp dirs and do not delete them. [ False ]')

  def _command_git_repo_script(self, command, *args, **kargs):
    from .git_repo_script_cli_command import git_repo_script_cli_command
    return git_repo_script_cli_command.handle_command(command, **kargs)
