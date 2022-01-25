#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check

from .file_duplicates import file_duplicates
from .file_duplicates_options import file_duplicates_options
from .file_check import file_check
from .file_util import file_util

class file_duplicates_cli_handler(cli_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super(file_duplicates_cli_handler, self).__init__(cli_args, options_class = file_duplicates_options)
    check.check_file_duplicates_options(self.options)
    self.options.sort_key = file_duplicates_options.sort_key
  
  def dups(self, files, delete):
    check.check_string_seq(files)
    check.check_bool(delete)

    dups = file_duplicates.find_duplicates(files, options = self.options)
    dup_filenames = []
    for item in dups.items:
      print(f'{item.filename}:')
      for dup in item.duplicates:
        print(f'  {dup}')
        dup_filenames.append(dup)

    if delete:
      if self.options.dry_run:
        for f in dup_filenames:
          print(f'DRY_RUN: delete {f}')
      else:
        file_util.remove(dup_filenames)
        
    return 0
