#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .git_cli_common_args import git_cli_common_args

class git_projects_cli_args(object):

  def __init__(self):
    pass
  
  def git_projects_add_args(self, subparser):

    # status
    p = subparser.add_parser('status', help = 'Print status for one or more git dirs.')
    self._git_projects_add_common_args(p)
    p.add_argument('dirs', action = 'store', nargs = '*', help = 'Dirs to check for status.')
    
  @classmethod
  def _git_projects_add_common_args(clazz, p):
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
                   help = 'Verbose output. [ None ]')
    p.add_argument('--debug', action = 'store_true', default = False,
                   help = 'Debug mode.  Save temporary files and downloads for debugging. [ None ]')
    p.add_argument('--no-remote-update', '-n', action = 'store_true',
                   help = 'Dont do remote update. [ False ]')
    p.add_argument('--show-untracked', '-u', action = 'store_true',
                   help = 'Include untracked git files. [ False ]')
    p.add_argument('--force-show', '-f',
                   action = 'store_true',
                   help = 'Force show of status even if there are no changes. [ False ]')
    p.add_argument('--jobs', '-j', action = 'store', type = int, default = 8, dest = 'num_jobs',
                   help = 'Number of jobs to run in parallel. [ 8 ]')

  def _command_git_projects(self, command, *args, **kargs):
    from .git_projects_cli_handler import git_projects_cli_handler
    return git_projects_cli_handler(kargs).handle_command(command)
