#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler

from ..system.check import check

from .dir_partition import dir_partition

class dir_partition_command_handler(bcli_command_handler):

  def name(self):
    return 'dir_partition'

  def _command_partition(self, files, options):
    check.check_string_seq(files)
    if options.dry_run:
      info = dir_partition.partition_info(files, options=options)
      for item in info.items:
        print('{} => {}'.format(item.src_filename, item.dst_filename))
    else:
      dir_partition.partition(files, options=options)
    return 0
