#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.files.bf_check import bf_check

from ..system.check import check

from .dir_split import dir_split

class dir_split_command_handler(bcli_command_handler):

  def name(self):
    return 'dir_split'

  def _command_split(self, src_dir, dst_dir, options):
    src_dir = bf_check.check_dir(src_dir)
    check.check_string(dst_dir)
    if options.dry_run:
      items = dir_split.split_items(src_dir, dst_dir, options)
      for item in items:
        print('{} => {}'.format(item.src_filename, item.dst_filename))
    else:
      dir_split.split(src_dir, dst_dir, options)
    return 0
