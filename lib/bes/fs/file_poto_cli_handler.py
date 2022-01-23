#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .file_poto import file_poto
from .file_poto_options import file_poto_options
from .file_check import file_check

class file_poto_cli_handler(cli_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super(file_poto_cli_handler, self).__init__(cli_args, options_class = file_poto_options)
    check.check_file_poto_options(self.options)
  
  def partition(self, dst_dir, files):
    check.check_string(dst_dir)
    check.check_string_seq(files)

    if self.options.dry_run:
      info = file_poto.partition_info(files, dst_dir, options = self.options)
      for item in info.items:
        print('{} => {}'.format(item.src_filename, item.dst_filename))
    else:
      file_poto.partition(files, dst_dir, options = self.options)
    return 0
