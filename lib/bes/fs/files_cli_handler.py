#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import binascii
from os import path

from ..bcli.bcli_deprecated_command_handler import bcli_deprecated_command_handler
from bes.common.algorithm import algorithm
from ..system.check import check
from bes.common.time_util import time_util
from bes.debug.hexdump import hexdump
from bes.version.semantic_version import semantic_version

from .dir_operation_item import dir_operation_item
from .dir_operation_item_list import dir_operation_item_list
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_find import file_find
from .file_mime import file_mime
from bes.files.bf_path import bf_path
from .file_resolver import file_resolver
from .file_split import file_split
from .file_util import file_util
from .filename_list import filename_list
from .files_cli_options import files_cli_options

class files_cli_handler(bcli_deprecated_command_handler):
  'dir project cli handler.'

  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = files_cli_options)
    check.check_files_cli_options(self.options)
  
  def checksums(self, files, algorithm):
    check.check_string_seq(files)

    files = file_resolver.resolve_files(files, options = self.options.file_resolver_options)
    for f in files:
      checksum = file_util.checksum(algorithm, f.filename_abs)
      print('{}: {}'.format(f.filename_abs, checksum))
    return 0

  def media_types(self, files):
    check.check_string_seq(files)

    files = file_resolver.resolve_files(files, options = self.options.file_resolver_options)
    for f in files:
      media_type = file_mime.media_type(f.filename_abs)
      print('{}: {}'.format(media_type, f.filename_abs))
    return 0

  def mime_types(self, files, cached):
    check.check_string_seq(files)
    check.check_bool(cached)

    files = file_resolver.resolve_files(files, options = self.options.file_resolver_options)
    for f in files:
      if cached:
        mime_type = file_attributes_metadata.get_mime_type(f.filename_abs)
      else:
        mime_type = file_mime.mime_type(f.filename_abs)
        
      print('{}: {}'.format(mime_type, f.filename_abs))
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
    
    files = file_resolver.resolve_files(files, options = self.options.file_resolver_options)
    for f in files:
      access = bf_path.access(f.filename_abs)
      print('{}: {}'.format(f.filename_abs, access))
    return 0
  
  def resolve(self, files):
    check.check_string_seq(files)

    files = file_resolver.resolve_files(files, options = self.options.file_resolver_options)
    for f in files:
      print(f'{f.filename_abs}')
    return 0
    
  def prefixes(self, files):
    check.check_string_seq(files)

    files = file_resolver.resolve_files(files, options = self.options.file_resolver_options)
    prefixes = filename_list.prefixes([ f.filename_abs for f in files ])
    for prefix in sorted(list(prefixes)):
      print(prefix)
    return 0

  def dup_basenames(self, files):
    check.check_string_seq(files)

    resolved_files = file_resolver.resolve_files(files, options = self.options.file_resolver_options)
    dmap = resolved_files.duplicate_basename_map()
    for basename, dup_files in sorted(resolved_files.duplicate_basename_map().items()):
      print(f'{basename}:')
      for dup_file in dup_files:
        print(f'  {dup_file}')
    return 0

  def cat(self, files, sort, output_filename):
    check.check_string_seq(files)
    check.check_bool(sort)
    check.check_string(output_filename, allow_none = True)

    resolved_files = file_resolver.resolve_files(files, options = self.options.file_resolver_options)
    files = resolved_files.absolute_files(sort = False)
    assert files
    if sort:
      files = semantic_version.sort_string_list(files)
    output_filename = output_filename or self._make_output_filename(files)
    file_split.unsplit_files(output_filename, files)
    for f in files:
      file_util.remove(f)
    return 0

  def move(self, src_dir, dst_dir):
    src_dir = file_check.check_dir(src_dir)
    dst_dir = file_check.check_dir(dst_dir)

    if src_dir == dst_dir:
      print(f'src_dir and dst_dir cannot be the same.')
      return 1
    
    resolved_files = file_resolver.resolve_files([ src_dir ], options = self.options.file_resolver_options)

    items = dir_operation_item_list()
    for resolved_file in resolved_files:
      src_filename = resolved_file.filename_abs
      dst_filename = path.join(dst_dir, resolved_file.filename)
      item = dir_operation_item(src_filename, dst_filename)
      items.append(item)

    if self.options.dry_run:
      resolved_items = items.resolve_for_move(self.options.dup_file_timestamp,
                                              self.options.dup_file_count)
      for i, item in enumerate(resolved_items, start = 1):
        print(f'DRY_RUN: {item.src_filename} => {item.dst_filename}')
      return 0

    items.move_files(self.options.dup_file_timestamp,
                     self.options.dup_file_count)

    file_find.remove_empty_dirs(src_dir)
    
    return 0
  
  @classmethod
  def _make_output_filename(clazz, files):
    prefix = files.common_prefix()
    if prefix:
      return prefix
    return files[0] + '.cat'

  def delete(self, files, from_file):
    check.check_string_seq(files)
    check.check_string(from_file, allow_none = True)

    if not files and not from_file:
      print(f'need to provide at least one filename')
      return 1

    from_file_files = []
    if from_file:
      with open(from_file, 'r') as fin:
        lines = fin.readlines()
        from_file_files = [ line.strip() for line in lines ]
        from_file_files = [ f for f in from_file_files if f ]
    
    cli_files = list(file_resolver.resolve_files(files, options = self.options.file_resolver_options).absolute_files())
    files = sorted(list(set(from_file_files + cli_files)))
    for f in files:
      if self.options.dry_run:
        print(f'DRY_RUN: would remove {f}')
      else:
        file_util.remove(f)
    return 0
