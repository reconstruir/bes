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
  
  def dups(self, files, delete):
    check.check_string_seq(files)
    check.check_bool(delete)

    dups = file_poto.find_duplicates(files, options = self.options)
    for item in dups.items:
      print(f'{item}')
#      for f in item.duplicates:
#        print(f'  {f}')
#        if delete:
#          if self.options.dry_run:
    return 0
