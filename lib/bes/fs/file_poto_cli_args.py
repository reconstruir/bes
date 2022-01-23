#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class file_poto_cli_args(object):

  def __init__(self):
    pass
  
  def file_poto_add_args(self, subparser):
    # partition
    p = subparser.add_parser('partition', help = 'Partition a directory into many directories.')
    self.__file_poto_cli_add_add_common_args(p)
    p.add_argument('dst_dir', action = 'store', default = None,
                   help = 'Destination directory [ None ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to partition [ None ]')
    p.add_argument('--type', action = 'store', default = 'prefix',
                   dest = 'partition_type',
                   help = 'Partition type to use [ None ]')
    p.add_argument('--threshold', action = 'store', default = 2,
                   type = int,
                   help = 'Threshold of files needed to partition a directory [ 2 ]')
    
  @classmethod
  def __file_poto_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Partition directories recursively [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    
  def _command_file_poto(self, command, *args, **kargs):
    from .file_poto_cli_handler import file_poto_cli_handler
    return file_poto_cli_handler(kargs).handle_command(command)
