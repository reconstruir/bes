#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import os
#from bes.common.check import check
#from bes.git.git_repo_script_options import git_repo_script_options
#from bes.git.git_clone_options import git_clone_options

#from .git_cli_command import git_cli_command

class git_identity_cli_args(object):

  def __init__(self):
    pass
  
  def git_identity_add_args(self, subparser):

    # git_identity_set
    p = subparser.add_parser('set', help = 'Set git identity.')
    p.add_argument('name', action = 'store', default = None, type = str,
                   help = 'The name of the git user. []')
    p.add_argument('email', action = 'store', default = None, type = str,
                   help = 'The email of the git user. []')
    
    # git_identity_get
    p = subparser.add_parser('get', help = 'Get the git identity.')
    p.add_argument('-n', '--name', action = 'store_true',
                   default = False, dest = 'name_only',
                   help = 'Print only the name. [ False ]')
    p.add_argument('-e', '--email', action = 'store_true',
                   default = False, dest = 'email_only',
                   help = 'Print only the email. [ False ]')
    
    # git_identity_ensure
    p = subparser.add_parser('ensure', help = 'Ensure that git identity is set or make it a default.')
    p.add_argument('name', action = 'store', default = None, type = str,
                   help = 'The name of the git user. []')
    p.add_argument('email', action = 'store', default = None, type = str,
                   help = 'The email of the git user. []')

  def _command_git_identity(self, command, *args, **kargs):
    from .git_identity_cli_command import git_identity_cli_command
    return git_identity_cli_command.handle_command(command, **kargs)
