#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..bcli.bcli_deprecated_command_handler import bcli_deprecated_command_handler
from ..system.check import check
from bes.common.algorithm import algorithm

from .file_check import file_check
from .file_duplicates import file_duplicates
from .file_duplicates_options import file_duplicates_options
from .file_find import file_find
from .file_util import file_util

class file_duplicates_cli_handler(bcli_deprecated_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = file_duplicates_options)
    check.check_file_duplicates_options(self.options)
  
  def dups(self, files, delete, keep_empty_dirs, blurber = None):
    files = file_check.check_file_or_dir_seq(files)
    check.check_bool(delete)
    check.check_bool(keep_empty_dirs)

    dups = file_duplicates.find_duplicates(files, options = self.options)
    dup_filenames = []
    for item in dups.items:
      if not self.options.quiet:
        print(f'{item.filename}:')
      for dup in item.duplicates:
        if not self.options.quiet:
          print(f'  {dup}')
        dup_filenames.append(dup)

    if delete:
      if self.options.dry_run:
        for f in dup_filenames:
          if blurber:
            blurber.blurb(f'DRY_RUN: delete {f}')
      else:
        file_util.remove(dup_filenames)
        if self.options.verbose:
          for f in dup_filenames:
            if blurber:
              blurber.blurb_verbose(f'DELETED file: {f}')
        if not keep_empty_dirs:
          fmap = dups.resolved_files.filename_abs_map()
          possible_empty_dir_roots = []
          for f in dup_filenames:
            item = fmap[f]
            possible_empty_dir_roots.append(item.root_dir)
          possible_empty_dir_roots = algorithm.unique(possible_empty_dir_roots)
          deleted_dirs = []
          for d in possible_empty_dir_roots:
            next_deleted_dirs = file_find.remove_empty_dirs(d)
            #print(f'next_deleted_dirs={next_deleted_dirs}')
            deleted_dirs.extend(next_deleted_dirs)
          if self.options.verbose:
            for d in deleted_dirs:
              if blurber:
                blurber.blurb_verbose(f'DELETED empty dir: {d}')
    return 0
