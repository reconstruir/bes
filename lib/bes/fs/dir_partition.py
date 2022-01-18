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

from .dir_partition_type import dir_partition_type
from .dir_partition_options import dir_partition_options
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_path import file_path
from .file_util import file_util
from .filename_list import filename_list
from .dir_operation_util import dir_operation_util


class dir_partition(object):
  'A class to partition directories'

  _log = logger('dir_partition')

  @classmethod
  def partition(clazz, files, dst_dir, options = None):
    check.check_dir_partition_options(options, allow_none = True)

    dst_dir_abs = path.abspath(dst_dir)

    options = options or dir_partition_options()
    items = clazz.partition_info(files, dst_dir_abs, options)

    dir_operation_util.move_files(items,
                                  options.dup_file_timestamp,
                                  options.dup_file_count)
      
  _file_info = namedtuple('_file_info', 'filename')
  _partition_item = namedtuple('_partition_item', 'src_filename, dst_filename')
  _partition_items_info = namedtuple('_partition_items_info', 'items, existing_split_dirs, possible_empty_dirs_roots')
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
    result = []
    for prefix, filenames in buckets.items():
      num_files = len(filenames)
      if num_files >= options.threshold:
        for src_filename in filenames:
          dst_filename = path.join(dst_dir, prefix, path.basename(src_filename))
          item = clazz._partition_item(src_filename, dst_filename)
          result.append(item)
    return result

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
            new_item = clazz._partition_item(item.src_filename,
                                         new_dst_filename,
                                         item.chunk_number,
                                         item.dst_basename)
            result.append(new_item)
      else:
        for _, items in media_type_map.items():
          result.extend(items)
    return result
'''
