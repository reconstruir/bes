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
from .dir_operation_util import dir_operation_util
from .dir_partition_options import dir_partition_options
from .dir_partition_type import dir_partition_type
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_find import file_find
from .file_path import file_path
from .file_util import file_util
from .filename_list import filename_list

class dir_partition(object):
  'A class to partition directories'

  _log = logger('dir_partition')

  @classmethod
  def partition(clazz, files, dst_dir, options = None):
    check.check_dir_partition_options(options, allow_none = True)

    dst_dir_abs = path.abspath(dst_dir)

    options = options or dir_partition_options()
    items, resolved_files = clazz.partition_info(files, dst_dir_abs, options)
    dir_operation_util.move_files(items,
                                  options.dup_file_timestamp,
                                  options.dup_file_count)
    root_dirs = resolved_files.root_dirs()
    for next_possible_empty_root in root_dirs:
      file_find.remove_empty_dirs(next_possible_empty_root)
      
  _partition_info_result = namedtuple('_partition_items_info', 'items, resolved_files, possible_empty_dirs_roots')
  @classmethod
  def partition_info(clazz, files, dst_dir, options):
    if options.partition_type == None:
      return items
    elif options.partition_type == dir_partition_type.MEDIA_TYPE:
      result = clazz._partition_info_by_media_type(files, dst_dir, options)
    elif options.partition_type == dir_partition_type.PREFIX:
      result = clazz._partition_info_by_prefix(files, dst_dir, options)
    else:
      assert False
    return result

  @classmethod
  def _partition_info_by_prefix(clazz, files, dst_dir, options):
    resolver_options = file_resolver_options(sort_order = 'depth',
                                             sort_reverse = True)
    resolved_files = file_resolver.resolve_files(files, options = resolver_options)
    basenames = resolved_files.basenames(sort = True)
    prefixes = filename_list.prefixes(basenames)
    buckets = clazz._make_buckets(prefixes, resolved_files.absolute_files(sort = True))
    items = dir_operation_item_list()
    for prefix, filenames in buckets.items():
      num_files = len(filenames)
      if num_files >= options.threshold:
        for src_filename in filenames:
          dst_filename = path.join(dst_dir, prefix, path.basename(src_filename))
          item = dir_operation_item(src_filename, dst_filename)
          items.append(item)
    return items, resolved_files

  @classmethod
  def _make_buckets(clazz, prefixes, files):
    buckets = {}
    for f in files:
      basename = path.basename(f)
      for prefix in prefixes:
        if basename.startswith(prefix):
          if not prefix in buckets:
            buckets[prefix] = []
          buckets[prefix].append(f)
    return buckets

  @classmethod
  def _partition_info_by_media_type(clazz, files, dst_dir, options):
    assert False
    
  '''
  @classmethod
  def _partition_partition_items_by_media_type(clazz, items):
    result = []
    dst_basename_map = clazz._make_dst_basename_map(items)
    for dst_basename, media_type_map in dst_basename_map.items():
      num_media_types = len(media_type_map)
      if num_media_types > 1:
        for media_type, items in media_type_map.items():
          for item in items:
            new_dst_filename = file_path.insert(item.dst_filename, -1, media_type)
            new_item = dir_operation_item(item.src_filename, new_dst_filename)
            result.append(new_item)
      else:
        for _, items in media_type_map.items():
          result.extend(items)
    return result
'''
