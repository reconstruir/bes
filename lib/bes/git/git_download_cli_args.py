#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .git_cli_common_args import git_cli_common_args

class git_download_cli_args(object):

  def __init__(self):
    pass
  
  def git_download_add_args(self, subparser):

    # download
    p = subparser.add_parser('download', help = 'Download.')
    self._git_download_add_common_args(p)
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('revision', action = 'store', default = None, type = str,
                   help = 'The revision to download. [ None ]')
    p.add_argument('-o', '--output', action = 'store', default = None, type = str, dest = 'output_filename',
                   help = 'Save the tarball to filename. [ ]')
    
    # available
    p = subparser.add_parser('available', help = 'List available revisions.')
    self._git_download_add_common_args(p)
    p.add_argument('address', action = 'store', type = str, default = None,
                   help = 'The git repo address to clone. [ None ]')
    p.add_argument('--prefix', action = 'store', default = None, type = str,
                   help = 'Show only tags with prefix. [ None ]')
    p.add_argument('--limit', action = 'store', default = None, type = int,
                   help = 'Limit number of tags shown. [ None ]')
    p.add_argument('--sort', action = 'store', default = 'version', dest = 'sort_type',
                   choices = ( 'lexical', 'version' ),
                   help = 'Sort type.  Either version or lexical. [ version ]')
    p.add_argument('--reverse', action = 'store_true', default = False,
                   help = 'Reverse the tag order such that greatest version is first. [ None ]')
    
  @classmethod
  def _git_download_add_common_args(clazz, p):
    from .git_repo_cli_args import git_repo_cli_args
    git_repo_cli_args._git_repo_add_clone_args(p)
    p.add_argument('--ssh-public-key', action = 'store', type = str, default = None,
                   help = 'The public ssh key. [ None ]')
    p.add_argument('--ssh-private-key', action = 'store', type = str, default = None,
                   help = 'The private ssh key. [ None ]')

  def _command_git_download(self, command, *args, **kargs):
    from .git_download_cli_handler import git_download_cli_handler
    return git_download_cli_handler(kargs).handle_command(command)
