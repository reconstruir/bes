#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class dir_partition_cli_args(object):

  def __init__(self):
    pass
  
  def dir_partition_add_args(self, subparser):
    # partition
    from .dir_partition_defaults import dir_partition_defaults
    p = subparser.add_parser('partition', help = 'Partition a directory into many directories.')
    self.__dir_partition_cli_add_add_common_args(p)
    p.add_argument('dst_dir', action = 'store', default = None,
                   help = 'Destination directory [ None ]')
    p.add_argument('files', action = 'store', default = [], nargs = '+',
                   help = 'One or more files or dirs to partition [ None ]')
    p.add_argument('--type', action = 'store',
                   default = dir_partition_defaults.PARTITION_TYPE, dest = 'partition_type',
                   help = 'Partition type to use [ None ]')
    p.add_argument('--threshold', action = 'store',
                   default = dir_partition_defaults.THRESHOLD,
                   type = int,
                   help = 'Threshold of files needed to partition a directory [ 2 ]')
    
  @classmethod
  def __dir_partition_cli_add_add_common_args(clazz, p):
    p.add_argument('--dry-run', action = 'store_true', default = False,
                   help = 'Dont do anything just print what would happen [ None ]')
    p.add_argument('-r', '--recursive', action = 'store_true', default = False,
                   help = 'Partition directories recursively [ None ]')
    p.add_argument('--verbose', action = 'store_true', default = False,
                   help = 'Verbose output [ False ]')
    
  def _command_dir_partition(self, command, *args, **kargs):
    from .dir_partition_cli_handler import dir_partition_cli_handler
    return dir_partition_cli_handler(kargs).handle_command(command)
