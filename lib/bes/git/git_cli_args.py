#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class git_cli_args(object):

  def __init__(self):
    pass
  
  def git_add_args(self, subparser):

    # git_tag
    p = subparser.add_parser('tag', help = 'Tag the repo locally and or remotely or just print the tags.')
    p.add_argument('--root-dir', action = 'store', default = None,
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
                   default = None,
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
                   default = None,
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
                   default = None,
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
                   default = None,
                   help = 'Root of repo to tag. [ . ]')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')
    p.add_argument('--prefix', action = 'store', default = None, type = str,
                   help = 'Show only tags with prefix. [ None ]')
    p.add_argument('--limit', action = 'store', default = None, type = int,
                   help = 'Limit number of tags shown. [ None ]')
    p.add_argument('--reverse', action = 'store_true', default = False,
                   help = 'Reverse the tag order such that greatest version is first. [ None ]')
    
    # git_branches
    p = subparser.add_parser('branches', help = 'List local and remote branches.')
    p.add_argument('--root-dir', action = 'store', default = None,
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

    # git_short
    p = subparser.add_parser('short', help = 'Print short commit hash.')
    p.add_argument('commit', action = 'store', type = str, default = None,
                   help = 'The git commit hash. [ None ]')
    p.add_argument('--root-dir', action = 'store', default = None,
                   help = 'The root dir of the git repo to archive. [ None ]')
    
    # git_long
    p = subparser.add_parser('long', help = 'Print long commit hash.')
    p.add_argument('commit', action = 'store', type = str, default = None,
                   help = 'The git commit hash. [ None ]')
    p.add_argument('--root-dir', action = 'store', default = None,
                   help = 'The root dir of the git repo to archive. [ None ]')

  def _command_git(self, command, *args, **kargs):
    from .git_cli_command import git_cli_command
    return git_cli_command.handle_command(command, **kargs)
    

  '''
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
