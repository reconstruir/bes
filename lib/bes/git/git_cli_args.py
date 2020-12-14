#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from bes.common.check import check
from bes.git.git_repo_script_options import git_repo_script_options
from bes.git.git_clone_options import git_clone_options

from .git_cli_command import git_cli_command

class git_cli_args(object):

  def __init__(self):
    pass
  
  def git_add_args(self, subparser):

    default_root = os.getcwd()
    default_working_dir = os.path.join(os.getcwd(), '.ego_git_repo_document_db_tmp')

    # git_set_identity
    p = subparser.add_parser('set_identity', help = 'Set git identity.')
    p.add_argument('--name', action = 'store', default = git_cli_command.DEFAULT_NAME, type = str,
                   help = 'The name of the git user. [ %s ]' % (git_cli_command.DEFAULT_NAME))
    p.add_argument('--email', action = 'store', default = git_cli_command.DEFAULT_EMAIL, type = str,
                   help = 'The email of the git user. [ %s ]' % (git_cli_command.DEFAULT_EMAIL))
    
    # git_get_identity
    p = subparser.add_parser('get_identity', help = 'Get the git identity.')
    p.add_argument('--name', action = 'store_true', default = False,
                   help = 'Print only the name. [ False ]')
    p.add_argument('--email', action = 'store_true', default = False,
                   help = 'Print only the email. [ False ]')
    
    # git_ensure_identity
    p = subparser.add_parser('ensure_identity', help = 'Ensure that git identity is set or make it a default.')

    # git_tag
    p = subparser.add_parser('tag', help = 'Tag the repo locally and or remotely or just print the tags.')
    p.add_argument('--root-dir', action = 'store', default = default_root,
                   help = 'Root of repo to tag. [ . ]')
    p.add_argument('tag', action = 'store', nargs = '?',
                   help = 'The tag to use or None to just print it. [ None ]')
    p.add_argument('--commit', action = 'store', type = str,
                   help = 'Use this commit hash instead of HEAD. [ None ]')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')
    
    # git_retag
    p = subparser.add_parser('retag', help = 'Delete the current latest tag and retag with the same tag.')
    p.add_argument('--root-dir',
                   action = 'store',
                   default = default_root,
                   help = 'Root of repo to tag. [ . ]')
    p.add_argument('tag',
                   action = 'store',
                   nargs = '?',
                   help = 'The tag to use or None to choose the last tag. [ None ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   help = 'Verbose output.  Mostly for the results (git status and diff). [ False ]')
    
    # git_bump_tag
    p = subparser.add_parser('bump_tag', help = 'Bump the tag version and tag.')
    p.add_argument('--component',
                   action = 'store',
                   type = str,
                   choices = ( 'major', 'minor', 'revision' ),
                   default = None,
                   help = 'What part of the version to bump. [ None ]')
    p.add_argument('--root-dir',
                   action = 'store',
                   default = default_root,
                   help = 'Root of repo to tag. [ . ]')
    p.add_argument('--dry-run',
                   action = 'store_true',
                   help = 'Dont do it just print it. [ False ]')
    p.add_argument('--dont-push',
                   action = 'store_true',
                   help = 'Dont push the new tag to the origin. [ False ]')
    p.add_argument('--reset-lower',
                   action = 'store_true',
                   help = 'Reset the lower components to zero. [ False ]')
    p.add_argument('-v', '--verbose', action = 'store_true',
                   help = 'Verbose output.  Mostly for the results (git status and diff). [ False ]')

    # git_delete_tags
    p = subparser.add_parser('delete_tags', help = 'Delete a tag locally and/or remotely.')
    p.add_argument('--root-dir',
                   action = 'store',
                   default = default_root,
                   help = 'Root of repo to tag. [ . ]')
    p.add_argument('tags', action = 'store', default = [], nargs = '*',
                   help = 'The end tags to delete. [ None ]')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')
    p.add_argument('--dry-run',
                   action = 'store_true',
                   help = 'Dont do anyting.  Just print what would happen. [ False ]')
    p.add_argument('--from-file', action = 'store',
                   help = 'Read the tags to delete from the given file. [ None ]')
    
    # git_tags
    p = subparser.add_parser('tags', help = 'List local and/or remote tags.')
    p.add_argument('--root-dir',
                   action = 'store',
                   default = default_root,
                   help = 'Root of repo to tag. [ . ]')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')

    # git_repo_greatest_tag
    p = subparser.add_parser('repo_greatest_tag', help = 'Print the greatest tag of an addressed repo numerically.')
    p.add_argument('address',
                   action = 'store',
                   type = str,
                   default = None,
                   help = 'The git repo address to clone. [ None ]')
    
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
    self._add_common_clone_args(p)

    # git_repo_clone
    p = subparser.add_parser('repo_clone', help = 'Clone a repo with nicer support for lfs and submodules.')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('dest_dir', action = 'store', type = str, default = None,
                   help = 'The dir to clone to. [ None ]')
    self._add_common_clone_args(p)
    
    # git_repo_sync
    p = subparser.add_parser('repo_sync', help = 'Sync a repo by either cloning or updating it including all its branches.')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('dest_dir', action = 'store', type = str, default = None,
                   help = 'The dir to clone to. [ None ]')
    self._add_common_clone_args(p)
    
    # branches
    p = subparser.add_parser('branches', help = 'List local and remote branches.')
    p.add_argument('--root-dir', action = 'store', default = default_root,
                   help = 'Root of repo to tag. [ . ]')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')
    p.add_argument('-b', '--brief', action = 'store_true', default = False,
                   help = 'Show only the branch names. [ False ]')
    p.add_argument('-p', '--plain', action = 'store_true', default = False,
                   help = 'Plain output instead of fancy. [ False ]')
    p.add_argument('-d', '--difference', action = 'store_true', default = False,
                   help = 'Show remote branches not already tracked locally. [ False ]')
    p.add_argument('-n', '--no-fetch', action = 'store_true', default = False,
                   help = 'Do not call git fetch first. [ False ]')

    # update_document
    p = subparser.add_parser('update_document', help = 'Update a document in a repo db.')
    p.add_argument('input_filename', action = 'store', type = str, default = None,
                   help = 'The file to store in the repo. [ None ]')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The repo address. [ None ]')
    p.add_argument('branch', action = 'store', type = str, default = None,
                   help = 'The branch to use. [ None ]')
    p.add_argument('-w', '--working-dir', action='store', default=default_working_dir,
                   help='Working directory used to clone git repos [ %s ]' % (
                     os.path.relpath(default_working_dir)))
    p.add_argument('--commit-msg', action = 'store', type = str, default = None,
                   help = 'The commit message for the check-in. [ None ]')
    self._add_common_clone_args(p)

    # load_document
    p = subparser.add_parser('load_document', help = 'Load a document that''s in a repo db.')
    p.add_argument('filename', action = 'store', type = str, default = None,
                   help = 'The name of the file in the repo. [ None ]')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The repo address. [ None ]')
    p.add_argument('branch', action = 'store', type = str, default = None,
                   help = 'The branch to use. [ None ]')
    p.add_argument('--output-filename', action = 'store', type = str, default = None,
                   help = 'Where to store the contents of the named file. [ ./filename ]')
    p.add_argument('-w', '--working-dir', action='store', default=default_working_dir,
                   help='Working directory used to clone git repos [ %s ]' % (
                     os.path.relpath(default_working_dir)))
    self._add_common_clone_args(p)

    # git_short
    p = subparser.add_parser('short', help = 'Print short commit hash.')
    p.add_argument('commit', action = 'store', type = str, default = None,
                   help = 'The git commit hash. [ None ]')
    p.add_argument('--root-dir', action = 'store', default = default_root,
                   help = 'The root dir of the git repo to archive. [ None ]')
    
    # git_long
    p = subparser.add_parser('long', help = 'Print long commit hash.')
    p.add_argument('commit', action = 'store', type = str, default = None,
                   help = 'The git commit hash. [ None ]')
    p.add_argument('--root-dir', action = 'store', default = default_root,
                   help = 'The root dir of the git repo to archive. [ None ]')

    # git_repo_lfs_invalid_files
    p = subparser.add_parser('lfs_invalid_files', help = 'Show invalid git lfs files in a repo.')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('-b', '--branch', action = 'store', type = str, default = 'master',
                   help = 'The branch to check. [ master ]')
    
  @classmethod
  def _add_common_clone_args(clazz, p):
    p.add_argument('--depth', action = 'store', type = int, default = None,
                   help = 'Clone depth. [ None ]')
    p.add_argument('--lfs', action = 'store_true', default = False,
                   help = 'Enable lfs when cloning. [ False ]')
    p.add_argument('--jobs', action = 'store', default = None,
                   help = 'Number of jobs when cloning submodules. [ False ]')
    p.add_argument('--submodules', action = 'store_true', default = False,
                   help = 'Whether to clone submodules. [ False ]')
    p.add_argument('--submodules-recursive', action = 'store_true', default = False,
                   help = 'Whether to clone submodules recursively. [ False ]')
    p.add_argument('--submodule-list', action = 'store', default = None,
                   help = 'List of submodules to clone (otherwise all get clones) [ None ]')
    p.add_argument('--branch', action = 'store', default = None,
                   help = 'The branch to checkout after cloning [ None ]')

  def _command_git_set_identity(self, name, email):
    return git_cli_command.set_identity(name, email)

  def _command_git_get_identity(self, name, email):
    return git_cli_command.get_identity(name, email)
  
  def _command_git_ensure_identity(self):
    return git_cli_command.ensure_identity()

  def _command_git_bump_tag(self, root_dir, component, dry_run, dont_push, reset_lower, verbose):
    return git_cli_command.bump_tag(root_dir, component, dry_run, dont_push, reset_lower, verbose)

  def _command_git_delete_tags(self, root_dir, tags, local, remote, dry_run, from_file):
    return git_cli_command.delete_tags(root_dir, tags, local, remote, dry_run, from_file)
  
  def _command_git_tags(self, root_dir, local, remote):
    return git_cli_command.list_tags(root_dir, local, remote)

  def _command_git_tag(self, root_dir, tag, local, remote, commit):
    return git_cli_command.tag(root_dir, tag, local, remote, commit)
  
  def _command_git_retag(self, root_dir, tag, verbose):
    return git_cli_command.retag(root_dir, tag = tag, verbose = verbose)

  def _command_git_repo_greatest_tag(self, address):
    return git_cli_command.repo_greatest_tag(address)

  def _command_git_repo_bump_tag(self, address, component, dry_run, reset_lower):
    return git_cli_command.repo_bump_tag(address, component, dry_run, reset_lower)

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

  def _command_git_update_document(self, input_filename, address, branch, working_dir, commit_msg):
    return git_cli_command.update_document(input_filename, address, branch, working_dir, commit_msg)

  def _command_git_load_document(self, filename, address, branch, output_filename, working_dir):
    return git_cli_command.load_document(filename, address, branch, output_filename, working_dir)

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
