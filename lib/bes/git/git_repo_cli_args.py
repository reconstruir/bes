#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.common.check import check
from bes.git.git_repo_script_options import git_repo_script_options
from bes.git.git_clone_options import git_clone_options

from .git_cli_command import git_cli_command

class git_repo_cli_args(object):

  def __init__(self):
    pass
  
  def git_repo_add_args(self, subparser):

    # git_repo_greatest_tag
    p = subparser.add_parser('repo_greatest_tag', help = 'Print the greatest tag of an addressed repo numerically.')
    p.add_argument('address',
                   action = 'store',
                   type = str,
                   default = None,
                   help = 'The git repo address to clone. [ None ]')
    self._git_repo_add_common_args(p)
    
    # git_repo_bump_tag
    p = subparser.add_parser('repo_bump_tag', help = 'Bump the tag of an addressed repo.')
    p.add_argument('address',
                   action = 'store',
                   type = str,
                   default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('--component',
                   action = 'store',
                   type = str,
                   choices = ( 'major', 'minor', 'revision' ),
                   default = None,
                   help = 'What part of the version to bump. [ None ]')
    p.add_argument('--dry-run',
                   action = 'store_true',
                   help = 'Dont do it just print it. [ False ]')
    p.add_argument('--reset-lower',
                   action = 'store_true',
                   help = 'Reset the lower components to zero. [ False ]')
    self._git_repo_add_common_args(p)
    
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
    self._git_repo_add_common_args(p)

    # git_repo_clone
    p = subparser.add_parser('repo_clone', help = 'Clone a repo with nicer support for lfs and submodules.')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('dest_dir', action = 'store', type = str, default = None,
                   help = 'The dir to clone to. [ None ]')
    self._git_repo_add_common_args(p)
    
    # git_repo_sync
    p = subparser.add_parser('repo_sync', help = 'Sync a repo by either cloning or updating it including all its branches.')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('dest_dir', action = 'store', type = str, default = None,
                   help = 'The dir to clone to. [ None ]')
    self._git_repo_add_common_args(p)
    
  @classmethod
  def _git_repo_add_common_args(clazz, p):
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
#    p.add_argument('--dry-run',
#                   action = 'store_true',
#                   help = 'Dont do it just print it. [ False ]')
#    p.add_argument('-v', '--verbose', action = 'store_true',
#                   help = 'Verbose output.  Mostly for the results (git status and diff). [ False ]')
#    p.add_argument('--debug', action = 'store_true',
#                   help = 'Debug mode.  Print out the tmp dirs and do not delete them. [ False ]')

  def _command_git_repo(self, command, *args, **kargs):
    from .git_repo_cli_command import git_repo_cli_command
    return git_repo_cli_command.handle_command(command, **kargs)

  '''
  def _command_git_repo_run_scripts(self, address, scripts, push, bump_tag_component, dry_run, debug,
                                    depth, lfs, jobs, submodules, submodules_recursive, submodule_list,
                                    verbose, branch):
    jobs, depth, submodule_list = self._resolve_clone_options(jobs, depth, submodule_list)
    options = git_repo_script_options(push = push,
                                      bump_tag_component = bump_tag_component,
                                      dry_run = dry_run,
                                      debug = debug,
                                      verbose = verbose,
                                      lfs = lfs,
                                      jobs = jobs,
                                      submodules = submodules,
                                      submodules_recursive = submodules_recursive,
                                      submodule_list = submodule_list,
                                      branch = branch)
    return git_cli_command.repo_run_scripts(address, scripts, options)

  def _command_git_branches(self, root_dir, local, remote, brief, plain, difference, no_fetch):
    return git_cli_command.branches(root_dir, local, remote, brief, plain, difference, no_fetch)

  def _command_git_short(self, root_dir, commit):
    return git_cli_command.short_commit(root_dir, commit)

  def _command_git_long(self, root_dir, commit):
    return git_cli_command.long_commit(root_dir, commit)
  
  def _command_git_repo_clone(self, address, dest_dir, depth, lfs, jobs, submodules,
                              submodules_recursive, submodule_list, branch):
    jobs, depth, submodule_list = self._resolve_clone_options(jobs, depth, submodule_list)
    options = git_clone_options(depth = depth,
                                lfs = lfs,
                                jobs = jobs,
                                submodules = submodules,
                                submodules_recursive = submodules_recursive,
                                submodule_list = submodule_list,
                                branch = branch)
    return git_cli_command.repo_clone(address, dest_dir, options)

  def _command_git_repo_sync(self, address, dest_dir, depth, lfs, jobs, submodules,
                              submodules_recursive, submodule_list, branch):
    jobs, depth, submodule_list = self._resolve_clone_options(jobs, depth, submodule_list)
    options = git_clone_options(depth = depth,
                                lfs = lfs,
                                jobs = jobs,
                                submodules = submodules,
                                submodules_recursive = submodules_recursive,
                                submodule_list = submodule_list,
                                branch = branch)
    return git_cli_command.repo_sync(address, dest_dir, options)

  @classmethod
  def _resolve_clone_options(clazz, jobs, depth, submodule_list):
    if jobs:
      jobs = int(jobs)
    if depth:
      depth = int(depth)
    if submodule_list:
      submodule_list = submodule_list.split(',')
    return jobs, depth, submodule_list
'''
  
