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

  def dup_basenames(self, files):
    check.check_string_seq(files)

    resolved_files = file_resolver.resolve_files(files, options = self._resolver_options)
    dmap = resolved_files.duplicate_basename_map()
    for basename, dup_files in sorted(resolved_files.duplicate_basename_map().items()):
      print(f'{basename}:')
      for dup_file in dup_files:
        print(f'  {dup_file}')
    return 0
  
