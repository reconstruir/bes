#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .git_cli_common_args import git_cli_common_args

class git_repo_cli_args(object):

  def __init__(self):
    pass
  
  def git_repo_add_args(self, subparser):

    # git_greatest_tag
    p = subparser.add_parser('greatest_tag', help = 'Print the greatest tag of an addressed repo numerically.')
    self._git_repo_add_common_args(p)
    
    # git_bump_tag
    p = subparser.add_parser('bump_tag', help = 'Bump the tag of an addressed repo.')
    self._git_repo_add_common_args(p)
    p.add_argument('--component', action = 'store', type = str, default = None,
                   choices = ( 'major', 'minor', 'revision' ),
                   help = 'What part of the version to bump. [ None ]')
    p.add_argument('--reset-lower', action = 'store_true',
                   help = 'Reset the lower components to zero. [ False ]')
    
    # git_clone
    p = subparser.add_parser('clone', help = 'Clone a repo with nicer support for lfs and submodules.')
    self._git_repo_add_common_args(p)
    p.add_argument('dest_dir', action = 'store', type = str, default = None,
                   help = 'The dir to clone to. [ None ]')
    
    # git_sync
    p = subparser.add_parser('sync', help = 'Sync a repo by either cloning or updating it including all its branches.')
    self._git_repo_add_common_args(p)
    p.add_argument('dest_dir', action = 'store', type = str, default = None,
                   help = 'The dir to clone to. [ None ]')
    
  @classmethod
  def _git_repo_add_common_args(clazz, p):
    git_cli_common_args.git_cli_add_common_args(p)
    clazz._git_repo_add_clone_args(p)
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')

  @classmethod
  def _git_repo_add_clone_args(clazz, p):
    p.add_argument('--depth', action = 'store', type = int, default = None,
                   help = 'Clone depth. [ None ]')
    p.add_argument('--lfs', action = 'store_true', default = False,
                   help = 'Enable lfs when cloning. [ False ]')
    p.add_argument('--jobs', action = 'store', default = None, type = int,
                   help = 'Number of jobs when cloning submodules. [ False ]')
    p.add_argument('--submodules', action = 'store_true', default = False,
                   help = 'Whether to clone submodules. [ False ]')
    p.add_argument('--submodules-recursive', action = 'store_true', default = False,
                   help = 'Whether to clone submodules recursively. [ False ]')
    p.add_argument('--submodule-list', action = 'store', default = None,
                   help = 'List of submodules to clone (otherwise all get cloned) [ None ]')
    p.add_argument('--branch', action = 'store', default = None,
                   help = 'The branch to checkout after cloning [ None ]')
    
  def _command_git_repo(self, command, *args, **kargs):
    from .git_repo_cli_handler import git_repo_cli_handler
    return git_repo_cli_handler(kargs).handle_command(command)
