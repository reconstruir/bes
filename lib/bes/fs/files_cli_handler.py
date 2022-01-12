#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import binascii
from os import path

from bes.cli.cli_command_handler import cli_command_handler
from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.debug.hexdump import hexdump

from .files_cli_options import files_cli_options
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_duplicates import file_duplicates
from .file_find import file_find
from .file_mime import file_mime
from .file_path import file_path
from .file_resolver import file_resolver
from .file_resolver_options import file_resolver_options
from .file_util import file_util
from .filename_list import filename_list

class files_cli_handler(cli_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super(files_cli_handler, self).__init__(cli_args, options_class = files_cli_options)
    check.check_files_cli_options(self.options)
    self._resolver_options = file_resolver_options(recursive = self.options.recursive)
  
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

    files = file_resolver.resolve_files(files, options = self._resolver_options)
    for f in files:
      checksum = file_util.checksum(algorithm, f.filename_abs)
      print('{}: {}'.format(f.filename_abs, checksum))
    return 0

  def media_types(self, files):
    check.check_string_seq(files)

    files = file_resolver.resolve_files(files, options = self._resolver_options)
    for f in files:
      media_type = file_mime.media_type(f.filename_abs)
      print('{}: {}'.format(media_type, f.filename_abs))
    return 0

  def mime_types(self, files):
    check.check_string_seq(files)

    files = file_resolver.resolve_files(files, options = self._resolver_options)
    for f in files:
      #mime_type = file_mime.mime_type(f.filename_abs)
      mime_type = file_attributes_metadata.get_mime_type(f.filename_abs)
      print('{}: {}'.format(mime_type, f.filename_abs))
    return 0
  
#file_attributes_metadata
  
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

  def check_access(self, files, level):
    check.check_string_seq(files)
    check.check_string_seq(levels)

    levels = algorithm.unique(levels)
    
    files = file_resolver.resolve_files(files, options = self._resolver_options)
    for f in files:
      access = file_path.access(f.filename_abs)
      print('{}: {}'.format(f.filename_abs, access))
    return 0
  
  def resolve(self, files):
    check.check_string_seq(files)

    files = file_resolver.resolve_files(files, options = self._resolver_options)
    for f in files:
      print(f'{f.filename_abs}')
    return 0
    
  def prefixes(self, files):
    check.check_string_seq(files)

    files = file_resolver.resolve_files(files, options = self._resolver_options)
    prefixes = filename_list.prefixes([ f.filename_abs for f in files ])
    for prefix in sorted(list(prefixes)):
      print(prefix)
    return 0
