#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class dirs_cli_args(object):

  def __init__(self):
    pass
  
  def dirs_add_args(self, subparser):
    # remove_empty
    p = subparser.add_parser('remove_empty', help = 'Remove empty directories.')
    self.__dirs_cli_add_add_common_args(p)
    p.add_argument('where', action = 'store', type = str, default = None,
                   help = 'Root directory where to start looking for empty dirs [ None ]')

  @classmethod
  def __dirs_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Find dirs recursively [ False ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    
  def _command_dirs(self, command, *args, **kargs):
    from .dirs_cli_handler import dirs_cli_handler
    return dirs_cli_handler(kargs).handle_command(command)
