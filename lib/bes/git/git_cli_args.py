#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .git_cli_common_args import git_cli_common_args

class git_cli_args(object):

  def __init__(self):
    pass
  
  def git_add_args(self, subparser):

    # git_tag
    p = subparser.add_parser('tag', help = 'Tag the repo locally and or remotely or just print the tags.')
    p.add_argument('tag', action = 'store', nargs = '?',
                   help = 'The tag to use or None to just print it. [ None ]')
    p.add_argument('--commit', action = 'store', type = str,
                   help = 'Use this commit hash instead of HEAD. [ None ]')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')
    p.add_argument('--annotate', action = 'store', type = str,
                   dest = 'annotation',
                   help = 'Annotate the tag with the given message. [ None ]')
    self._git_add_common_args(p)
    
    # git_retag
    p = subparser.add_parser('retag', help = 'Delete the current latest tag and retag with the same tag.')
    p.add_argument('tag', action = 'store', nargs = '?',
                   help = 'The tag to use or None to choose the last tag. [ None ]')
    self._git_add_common_args(p)
    
    # git_bump_tag
    p = subparser.add_parser('bump_tag', help = 'Bump the tag version and tag.')
    p.add_argument('--component', action = 'store', type = str, default = None,
                   choices = ( 'major', 'minor', 'revision' ),
                   help = 'What part of the version to bump. [ None ]')
    p.add_argument('--dont-push', action = 'store_true',
                   help = 'Dont push the new tag to the origin. [ False ]')
    p.add_argument('--reset-lower', action = 'store_true',
                   help = 'Reset the lower components to zero. [ False ]')
    p.add_argument('--prefix', action = 'store', type = str, default = None,
                   help = 'Optional tag prefix. [ None ]')
    self._git_add_common_args(p)

    # git_delete_tags
    p = subparser.add_parser('delete_tags', help = 'Delete a tag locally and/or remotely.')
    p.add_argument('tags', action = 'store', default = [], nargs = '*',
                   help = 'The end tags to delete. [ None ]')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')
    p.add_argument('--from-file', action = 'store',
                   help = 'Read the tags to delete from the given file. [ None ]')
    self._git_add_common_args(p)
    
    # git_tags
    p = subparser.add_parser('tags', help = 'List local and/or remote tags.')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')
    p.add_argument('--prefix', action = 'store', default = None, type = str,
                   help = 'Show only tags with prefix. [ None ]')
    p.add_argument('--limit', action = 'store', default = None, type = int,
                   help = 'Limit number of tags shown. [ None ]')
    p.add_argument('--sort', action = 'store', default = 'version', dest = 'sort_type',
                   choices = ( 'lexical', 'version' ),
                   help = 'Sort type.  Either version or lexical. [ version ]')
    p.add_argument('--reverse', action = 'store_true', default = False,
                   help = 'Reverse the tag order such that greatest version is first. [ None ]')
    self._git_add_common_args(p)
    
    # git_branches
    p = subparser.add_parser('branches', help = 'List local and remote branches.')
    p.add_argument('-l', '--local', action = 'store_true', default = None,
                   help = 'Show local tags. [ False ]')
    p.add_argument('-r', '--remote', action = 'store_true', default = None,
                   help = 'Show remote tags. [ False ]')
    p.add_argument('-d', '--difference', action = 'store_true', default = False,
                   help = 'Show remote branches not already tracked locally. [ False ]')
    p.add_argument('-n', '--no-fetch', action = 'store_true', default = False,
                   help = 'Do not call git fetch first. [ False ]')
    self._git_add_common_args(p)

    # git_short
    p = subparser.add_parser('short', help = 'Print short commit hash.')
    p.add_argument('commit', action = 'store', type = str, default = None,
                   help = 'The git commit hash. [ None ]')
    self._git_add_common_args(p)
    
    # git_long
    p = subparser.add_parser('long', help = 'Print long commit hash.')
    p.add_argument('commit', action = 'store', type = str, default = None,
                   help = 'The git commit hash. [ None ]')
    self._git_add_common_args(p)

  @classmethod
  def _git_add_common_args(clazz, p):
    p.add_argument('--root-dir', action = 'store', default = None,
                   help = 'The root dir of the git repo to archive. [ None ]')
    git_cli_common_args.git_cli_add_common_args(p)
    
  def _command_git(self, command, *args, **kargs):
    from .git_cli_command import git_cli_command
    return git_cli_command(kargs).handle_command(command)
