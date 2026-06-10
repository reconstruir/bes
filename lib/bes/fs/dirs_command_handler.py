#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.files.bf_check import bf_check

from .file_find import file_find

class dirs_command_handler(bcli_command_handler):

  def name(self):
    return 'dirs'

  def _command_remove_empty(self, where, dry_run, recursive, options):
    where = bf_check.check_dir(where)
    max_depth = None if recursive else 1
    if dry_run:
      empties = file_find.find_empty_dirs(where, relative=False, max_depth=max_depth)
      for empty in empties:
        print(f'DRY_RUN: would remove {empty}')
    else:
      file_find.remove_empty_dirs(where, max_depth=max_depth)
    return 0
