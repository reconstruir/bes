#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler

from ..system.check import check

from .dir_combine import dir_combine

class dir_combine_command_handler(bcli_command_handler):

  def name(self):
    return 'dir_combine'

  def _command_combine(self, files, options):
    check.check_string_seq(files)
    if options.dry_run:
      info = dir_combine.combine_info(files, options=options)
      for item in info.items:
        print('{} => {}'.format(item.src_filename, item.dst_filename))
    else:
      dir_combine.combine(files, options=options)
    return 0
