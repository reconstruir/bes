#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.common.check import check
from bes.git.git_repo_script_options import git_repo_script_options
from bes.git.git_clone_options import git_clone_options

from .git_cli_handler import git_cli_handler

class git_repo_document_cli_args(object):

  def __init__(self):
    pass
  
  def git_repo_document_add_args(self, subparser):

    default_root = os.getcwd()
    default_working_dir = os.path.join(os.getcwd(), '.ego_git_repo_document_db_tmp')

    # update
    p = subparser.add_parser('update', help = 'Update a document in a repo db.')
    p.add_argument('input_filename', action = 'store', type = str, default = None,
                   help = 'The file to store in the repo. [ None ]')
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The repo address. [ None ]')
    p.add_argument('branch', action = 'store', type = str, default = None,
                   help = 'The branch to use. [ None ]')
    p.add_argument('-w', '--working-dir', action='store', default = default_working_dir,
                   help='Working directory used to clone git repos [ %s ]' % (
                     os.path.relpath(default_working_dir)))
    p.add_argument('--commit-msg', action = 'store', type = str, default = None,
                   help = 'The commit message for the check-in. [ None ]')

    # load
    p = subparser.add_parser('load', help = 'Load a document that''s in a repo db.')
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

  def _command_git_repo_document(self, command, *args, **kargs):
    from .git_repo_document_cli_handler import git_repo_document_cli_handler
    return git_repo_document_cli_handler.handle_command(command, **kargs)
