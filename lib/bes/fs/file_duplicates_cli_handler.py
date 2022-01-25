#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .file_duplicates import file_duplicates
from .file_duplicates_options import file_duplicates_options
from .file_check import file_check

class file_duplicates_cli_handler(cli_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super(file_duplicates_cli_handler, self).__init__(cli_args, options_class = file_duplicates_options)
    check.check_file_duplicates_options(self.options)
  
  def dups(self, files, delete):
    check.check_string_seq(files)
    check.check_bool(delete)

    dups = file_duplicates.find_duplicates(files, options = self.options)
    for item in dups.items:
      print(f'{item.filename}:')
      for dup in item.duplicates:
        print(f'  {dup}')
    return 0
