#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.fs.file_check import file_check

from .dir_split import dir_split

class dir_cli_handler(cli_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super(dir_cli_handler, self).__init__(cli_args)
    
  def split(self, src_dir, dst_dir, chunk_size, prefix):
    src_dir = file_check.check_dir(src_dir)
    check.check_string(dst_dir)
    check.check_int(chunk_size)
    check.check_string(prefix)

    dir_split.split(src_dir, dst_dir, chunk_size, prefix)
    return 0
