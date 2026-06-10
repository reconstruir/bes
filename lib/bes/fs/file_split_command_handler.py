#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler

from ..system.check import check

from .file_split import file_split

class file_split_command_handler(bcli_command_handler):

  def name(self):
    return 'file_split'

  def _command_unsplit(self, files, options):
    check.check_string_seq(files)
    if options.dry_run:
      info = file_split.find_and_unsplit_info(files, options=options)
      for item in info.items:
        print(f'{item.target}:')
        for filename in item.files:
          print(f'  {filename}')
    else:
      file_split.find_and_unsplit(files, options=options)
    return 0
