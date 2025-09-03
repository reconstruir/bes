#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.common.algorithm import algorithm
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.system.check import check
from bes.system.log import logger
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options

from .dir_operation_item import dir_operation_item
from .dir_operation_item_list import dir_operation_item_list
from .dir_combine_options import dir_combine_options
from .dir_combine_type import dir_combine_type
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_find import file_find
from bes.files.bf_path import bf_path
from .file_util import file_util
from .dir_util import dir_util
from .filename_list import filename_list

class dir_combine(object):
  'A class to combine directories'

  _log = logger('dir_combine')

  @classmethod
  def combine(clazz, files, options = None):
    check.check_string_seq(files)
    check.check_dir_combine_options(options, allow_none = True)

    options = options or dir_combine_options()

    info = clazz.combine_info(files, options = options)
    info.items.move_files(options.dup_file_timestamp,
                          options.dup_file_count)
    root_dirs = info.resolved_files.root_dirs()
    for next_possible_empty_root in root_dirs:
      file_find.remove_empty_dirs(next_possible_empty_root)
      
  _combine_info_result = namedtuple('_combine_info_result', 'items, resolved_files')
  @classmethod
  def combine_info(clazz, files, options = None):
    check.check_string_seq(files)
    check.check_dir_combine_options(options, allow_none = True)

    options = options or dir_combine_options()

    if options.ignore_empty:
      should_ignore = lambda d: not path.exists(d) or dir_util.is_empty(d)
      files = [ f for f in files if not should_ignore(f) ]
      
    resolved_files = clazz._resolve_files(files, options.recursive)
    if not resolved_files:
      return clazz._combine_info_result(dir_operation_item_list(), resolved_files)
    destination_dir = options.destination_dir or resolved_files[0].dirname
    destination_dir_abs = path.abspath(destination_dir)

    items = dir_operation_item_list()
    for resolved_file in resolved_files:
      src_filename = resolved_file.filename_abs
      if options.flatten:
        src_basename = path.basename(src_filename)
      else:
        src_basename = resolved_file.filename
      dst_filename = path.join(destination_dir_abs, src_basename)
      item = dir_operation_item(src_filename, dst_filename)
      items.append(item)
    return clazz._combine_info_result(items, resolved_files)

  @classmethod
  def _resolve_files(clazz, files, recursive):
    resolver_options = file_resolver_options(sort_order = 'depth',
                                             sort_reverse = True,
                                             recursive = recursive)
    return file_resolver.resolve_files(files, options = resolver_options)
