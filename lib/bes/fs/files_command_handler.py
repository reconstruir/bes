#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.common.algorithm import algorithm
from bes.debug.hexdump import hexdump
from bes.files.bf_check import bf_check
from bes.files.bf_file_ops import bf_file_ops
from bes.files.bf_path import bf_path
from bes.files.checksum.bf_checksum import bf_checksum
from bes.version.semantic_version import semantic_version

from ..system.check import check

from .dir_operation_item import dir_operation_item
from .dir_operation_item_list import dir_operation_item_list
from .file_attributes_metadata import file_attributes_metadata
from .file_find import file_find
from .file_mime import file_mime
from .file_resolver import file_resolver
from .file_split import file_split
from .filename_list import filename_list

class files_command_handler(bcli_command_handler):

  def name(self):
    return 'files'

  def _command_checksums(self, files, algorithm, options):
    check.check_string_seq(files)
    resolved = file_resolver.resolve_files(files, options=options.file_resolver_options)
    for f in resolved:
      checksum = bf_checksum.checksum(f.filename_abs, algorithm)
      print('{}: {}'.format(f.filename_abs, checksum))
    return 0

  def _command_media_types(self, files, options):
    check.check_string_seq(files)
    resolved = file_resolver.resolve_files(files, options=options.file_resolver_options)
    for f in resolved:
      media_type = file_mime.media_type(f.filename_abs)
      print('{}: {}'.format(media_type, f.filename_abs))
    return 0

  def _command_mime_types(self, files, cached, options):
    check.check_string_seq(files)
    check.check_bool(cached)
    resolved = file_resolver.resolve_files(files, options=options.file_resolver_options)
    for f in resolved:
      if cached:
        mime_type = file_attributes_metadata.get_mime_type(f.filename_abs)
      else:
        mime_type = file_mime.mime_type(f.filename_abs)
      print('{}: {}'.format(mime_type, f.filename_abs))
    return 0

  def _command_hexify(self, filename, options):
    filename = bf_check.check_file(filename)
    dump = hexdump.filename(filename, line_delimiter='\n')
    print(dump)
    return 0

  def _command_check_access(self, files, levels, options):
    check.check_string_seq(files)
    levels = algorithm.unique(levels)
    resolved = file_resolver.resolve_files(files, options=options.file_resolver_options)
    for f in resolved:
      access = bf_path.access(f.filename_abs)
      print('{}: {}'.format(f.filename_abs, access))
    return 0

  def _command_resolve(self, files, options):
    check.check_string_seq(files)
    resolved = file_resolver.resolve_files(files, options=options.file_resolver_options)
    for f in resolved:
      print(f'{f.filename_abs}')
    return 0

  def _command_prefixes(self, files, options):
    check.check_string_seq(files)
    resolved = file_resolver.resolve_files(files, options=options.file_resolver_options)
    prefixes = filename_list.prefixes([f.filename_abs for f in resolved])
    for prefix in sorted(list(prefixes)):
      print(prefix)
    return 0

  def _command_dup_basenames(self, files, options):
    check.check_string_seq(files)
    resolved = file_resolver.resolve_files(files, options=options.file_resolver_options)
    for basename, dup_files in sorted(resolved.duplicate_basename_map().items()):
      print(f'{basename}:')
      for dup_file in dup_files:
        print(f'  {dup_file}')
    return 0

  def _command_cat(self, files, sort, output_filename, options):
    check.check_string_seq(files)
    check.check_bool(sort)
    check.check_string(output_filename, allow_none=True)
    resolved = file_resolver.resolve_files(files, options=options.file_resolver_options)
    abs_files = resolved.absolute_files(sort=False)
    assert abs_files
    if sort:
      abs_files = semantic_version.sort_string_list(abs_files)
    output_filename = output_filename or self._make_output_filename(abs_files)
    file_split.unsplit_files(output_filename, abs_files)
    for f in abs_files:
      bf_file_ops.remove(f)
    return 0

  def _command_move(self, src_dir, dst_dir, options):
    src_dir = bf_check.check_dir(src_dir)
    dst_dir = bf_check.check_dir(dst_dir)
    if src_dir == dst_dir:
      print('src_dir and dst_dir cannot be the same.')
      return 1
    resolved = file_resolver.resolve_files([src_dir], options=options.file_resolver_options)
    items = dir_operation_item_list()
    for resolved_file in resolved:
      src_filename = resolved_file.filename_abs
      dst_filename = path.join(dst_dir, resolved_file.filename)
      items.append(dir_operation_item(src_filename, dst_filename))
    if options.dry_run:
      resolved_items = items.resolve_for_move(options.dup_file_timestamp,
                                              options.dup_file_count)
      for item in resolved_items:
        print(f'DRY_RUN: {item.src_filename} => {item.dst_filename}')
      return 0
    items.move_files(options.dup_file_timestamp, options.dup_file_count)
    file_find.remove_empty_dirs(src_dir)
    return 0

  def _command_delete(self, files, from_file, options):
    check.check_string_seq(files)
    check.check_string(from_file, allow_none=True)
    if not files and not from_file:
      print('need to provide at least one filename')
      return 1
    from_file_files = []
    if from_file:
      with open(from_file, 'r') as fin:
        lines = fin.readlines()
        from_file_files = [line.strip() for line in lines]
        from_file_files = [f for f in from_file_files if f]
    cli_files = list(file_resolver.resolve_files(files,
                                                  options=options.file_resolver_options).absolute_files())
    all_files = sorted(list(set(from_file_files + cli_files)))
    for f in all_files:
      if options.dry_run:
        print(f'DRY_RUN: would remove {f}')
      else:
        bf_file_ops.remove(f)
    return 0

  @classmethod
  def _make_output_filename(clazz, files):
    prefix = files.common_prefix()
    if prefix:
      return prefix
    return files[0] + '.cat'
