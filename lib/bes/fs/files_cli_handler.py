#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import binascii
from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.check import check
from bes.debug.hexdump import hexdump

from .dir_split import dir_split
from .dir_split_options import dir_split_options
from .file_check import file_check
from .file_duplicates import file_duplicates
from .file_find import file_find
from .file_resolver import file_resolver
from .file_util import file_util

class files_cli_handler(cli_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super(files_cli_handler, self).__init__(cli_args, options_class = dir_split_options)
    check.check_dir_split_options(self.options)
  
  def split(self, src_dir, dst_dir):
    src_dir = file_check.check_dir(src_dir)
    check.check_string(dst_dir)

    if self.options.dry_run:
      items = dir_split.split_items(src_dir, dst_dir, self.options)
      for item in items:
        print('{} => {}'.format(item.src_filename, item.dst_filename))
    else:
      dir_split.split(src_dir, dst_dir, self.options)
    return 0

  def dups(self, dirs, delete):
    dirs = file_check.check_dir_seq(dirs)
    check.check_bool(delete)

    dups = file_duplicates.find_duplicates(dirs)
    for dup in dups:
      if self.options.dry_run:
        print('DRY_RUN: {}: {}'.format(dup.filename, ','.join(dup.duplicates)))
      else:
        file_util.remove(dup.duplicates)
    return 0

  def checksums(self, files, algorithm):
    check.check_string_seq(files)
    files = file_resolver.resolve_files(files, recursive = self.options.recursive)
    for f in files:
      checksum = file_util.checksum('sha256', f.filename_abs)
      print('{}: {}'.format(f.filename_abs, checksum))
    return 0
  
  def remove_empty(self, where):
    where = file_check.check_dir(where)
    max_depth = None if self.options.recursive else 1
    if self.options.dry_run:
      empties = file_find.find_empty_dirs(where, relative = False, max_depth = max_depth)
      for empty in empties:
        print(empty)
    else:
      file_find.remove_empty_dirs(where, max_depth = max_depth)
      
    return 0

  def hexify(self, filename):
    filename = file_check.check_file(filename)

    dump = hexdump.filename(filename, line_delimiter = '\n')
    print(dump)
    return 0
