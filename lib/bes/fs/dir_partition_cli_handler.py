#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..bcli.bcli_deprecated_command_handler import bcli_deprecated_command_handler
from ..system.check import check

from .dir_partition import dir_partition
from .dir_partition_options import dir_partition_options
from .file_check import file_check

class dir_partition_cli_handler(bcli_deprecated_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = dir_partition_options)
    check.check_dir_partition_options(self.options)
  
  def partition(self, files):
    check.check_string_seq(files)

    if self.options.dry_run:
      info = dir_partition.partition_info(files, options = self.options)
      for item in info.items:
        print('{} => {}'.format(item.src_filename, item.dst_filename))
    else:
      dir_partition.partition(files, options = self.options)
    return 0
