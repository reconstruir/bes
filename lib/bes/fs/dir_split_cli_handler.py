#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..bcli.bcli_deprecated_command_handler import bcli_deprecated_command_handler
from ..system.check import check

from .dir_split import dir_split
from .dir_split_options import dir_split_options
from .file_check import file_check

class dir_split_cli_handler(bcli_deprecated_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = dir_split_options)
    check.check_dir_split_options(self.options)
  
  def split(self, src_dir, dst_dir):
    src_dir = file_check.check_dir(src_dir)
    check.check_string(dst_dir)

    if self.options.dry_run:
      items = dir_split.split_items(src_dir, dst_dir, self.options)
      for item in items:
        print('{} => {}'.format(item.src_filename, item.dst_filename))
    else:
      dir_split.split(src_dir, dst_dir, self.options)
    return 0
