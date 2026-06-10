#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.common.algorithm import algorithm
from bes.files.bf_check import bf_check
from bes.files.bf_file_ops import bf_file_ops

from ..system.check import check

from .file_duplicates import file_duplicates
from .file_find import file_find

class file_duplicates_command_handler(bcli_command_handler):

  def name(self):
    return 'file_duplicates'

  def _command_dups(self, files, delete, keep_empty_dirs, options):
    files = bf_check.check_file_or_dir_seq(files)
    check.check_bool(delete)
    check.check_bool(keep_empty_dirs)
    dups = file_duplicates.find_duplicates(files, options=options)
    dup_filenames = []
    for item in dups.items:
      if not options.quiet:
        print(f'{item.filename}:')
      for dup in item.duplicates:
        if not options.quiet:
          print(f'  {dup}')
        dup_filenames.append(dup)
    if delete:
      if options.dry_run:
        for f in dup_filenames:
          print(f'DRY_RUN: delete {f}')
      else:
        bf_file_ops.remove(dup_filenames)
        if not keep_empty_dirs:
          fmap = dups.resolved_files.filename_abs_map()
          possible_empty_dir_roots = algorithm.unique(
            [fmap[f].root_dir for f in dup_filenames])
          for d in possible_empty_dir_roots:
            file_find.remove_empty_dirs(d)
    return 0
