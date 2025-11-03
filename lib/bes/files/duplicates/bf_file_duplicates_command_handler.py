#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass

from bes.system.check import check

from bes.bcli.bcli_command_handler import bcli_command_handler

from .bf_file_duplicates_finder import bf_file_duplicates_finder
from .bf_file_duplicates_command_options import bf_file_duplicates_command_options

class bf_file_duplicates_command_handler(bcli_command_handler):

  #@abc.abstractmethod
  def name(self):
    return 'bf_file_duplicates_finder'
  
  def _command_find(self, where, options):
    check.check_string_seq(where)
    check.check_bf_file_duplicates_command_options(options)

    print(f'where={where}')
    return 0
    def _progress_cb(progress):
      if progress.state == 'finding':
        self.blurb(f'{progress.index} of {progress.total}: {progress.entry.filename}')

    resolver_options = options.file_duplicates_options.clone()
    resolver_options.progress_callback = _progress_cb
      
    resolver = bf_file_duplicates_finder(options = resolver_options)
    entries = resolver.resolve(where)
    for entry in entries:
      print(entry.filename)
    return 0
  
  '''
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
'''  
