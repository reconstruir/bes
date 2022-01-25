#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.common.algorithm import algorithm

from .file_check import file_check
from .file_split import file_split
from .file_split_options import file_split_options
from .file_find import file_find
from .file_util import file_util

class file_split_cli_handler(cli_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super(file_split_cli_handler, self).__init__(cli_args, options_class = file_split_options)
    check.check_file_split_options(self.options)
    self.options.sort_key = file_split_options.sort_key
  
  def dups(self, files, delete, keep_empty_dirs):
    check.check_string_seq(files)
    check.check_bool(delete)
    check.check_bool(keep_empty_dirs)

    dups = file_split.find_duplicates(files, options = self.options)
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
        if self.options.verbose:
          for f in dup_filenames:
            print(f'DELETED file: {f}')
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
            deleted_dirs.extend(next_deleted_dirs)
          if self.options.verbose:
            for d in deleted_dirs:
              print(f'DELETED empty dir: {d}')
    return 0
