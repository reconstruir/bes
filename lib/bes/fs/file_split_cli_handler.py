#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..bcli.bcli_deprecated_command_handler import bcli_deprecated_command_handler
from ..system.check import check
from bes.common.algorithm import algorithm

from .file_check import file_check
from .file_split import file_split
from .file_split_options import file_split_options

class file_split_cli_handler(bcli_deprecated_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = file_split_options)
    check.check_file_split_options(self.options)
  
  def unsplit(self, files):
    check.check_string_seq(files)

    if self.options.dry_run:
      info = file_split.find_and_unsplit_info(files, options = self.options)
      for item in info.items:
        print(f'{item.target}:')
        for filename in item.files:
          print(f'  {filename}')
    else:
      file_split.find_and_unsplit(files, options = self.options)
    return 0
