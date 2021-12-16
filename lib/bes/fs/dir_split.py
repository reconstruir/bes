#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.common.algorithm import algorithm
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.system.check import check
from bes.system.log import logger

from .dir_sort_order import dir_sort_order
from .dir_split_options import dir_split_options
from .dir_util import dir_util
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_find import file_find
from .file_mime import file_mime
from .file_path import file_path
from .file_util import file_util

class dir_split(object):
  'A class to split directories'

  _log = logger('dir_split')

  @classmethod
  def split(clazz, src_dir, dst_dir, options = None):
    src_dir_abs = file_check.check_dir(src_dir)
    check.check_string(dst_dir)
    dst_dir_abs = path.abspath(dst_dir)
    check.check_dir_split_options(options, allow_none = True)

    options = options or dir_split_options()
    info = clazz._split_info(src_dir_abs, dst_dir_abs, options)

    clazz._move_files(info.items,
                      options.dup_file_timestamp,
                      options.dup_file_count)
    
    for d in info.existing_split_dirs:
      if dir_util.is_empty(d):
        dir_util.remove(d)

    for next_possible_empty_root in info.possible_empty_dirs_roots:
      file_find.remove_empty_dirs(next_possible_empty_root)

    file_find.remove_empty_dirs(dst_dir_abs)
      
  _file_info = namedtuple('_file_info', 'filename, media_type')
  _split_item = namedtuple('_split_item', 'src_filename, dst_filename, chunk_number, dst_basename, media_type')
  _split_items_info = namedtuple('_split_items_info', 'items, existing_split_dirs, possible_empty_dirs_roots')
  @classmethod
  def _split_info(clazz, src_dir, dst_dir, options):
    assert path.isabs(src_dir)
    assert path.isabs(dst_dir)

    old_files = []
    existing_split_dirs = clazz._existing_split_dirs(dst_dir, options.prefix)
    for old_dir in existing_split_dirs:
      old_files.extend(dir_util.list_files(old_dir))
    clazz._log.log_d('old_files={}'.format(old_files))
    
    options = options or dir_split_options()
    items = []
    if options.recursive:
      new_files = file_find.find(src_dir, relative = False, file_type = file_find.FILE)
      possible_empty_dirs_roots = []
      dirs = algorithm.unique([ path.dirname(f) for f in new_files ])
      for d in dirs:
        if d != src_dir:
          d_relative = file_util.remove_head(d, src_dir + path.sep)
          if not d_relative.startswith(options.prefix):
            d_root = path.join(src_dir, file_path.split(d_relative)[0])
            possible_empty_dirs_roots.append(d_root)
      possible_empty_dirs_roots = algorithm.unique(possible_empty_dirs_roots)
    else:
      new_files = dir_util.list_files(src_dir)
      possible_empty_dirs_roots = []
    
    files = algorithm.unique(old_files + new_files)
    file_info_list = clazz._make_file_info_list(files, options.partition)
    sorted_file_info_list = clazz._sort_file_info_list(file_info_list,
                                                       options.sort_order,
                                                       options.sort_reverse,
                                                       options.partition)
    chunks = [ chunk for chunk in object_util.chunks(sorted_file_info_list, options.chunk_size) ]
    num_chunks = len(chunks)
    num_digits = len(str(num_chunks))
    for chunk_number, chunk in enumerate(chunks, start = 1):
      dst_basename = '{}{}'.format(options.prefix, str(chunk_number).zfill(num_digits))
      chunk_dst_dir = path.join(dst_dir, dst_basename)
      for finfo in chunk:
        dst_filename = path.join(chunk_dst_dir, path.basename(finfo.filename))
        item = clazz._split_item(finfo.filename,
                                 dst_filename,
                                 chunk_number,
                                 dst_basename,
                                 finfo.media_type)
        items.append(item)
    if options.partition:
      items = clazz._partition_split_items(items)
    return clazz._split_items_info(items, existing_split_dirs, possible_empty_dirs_roots)

  @classmethod
  def split_items(clazz, src_dir, dst_dir, options = None):
    'Return a list of split items that when renaming each item implements split.'
    src_dir_abs = file_check.check_dir(src_dir)
    check.check_string(dst_dir)
    dst_dir_abs = path.abspath(dst_dir)
    check.check_dir_split_options(options, allow_none = True)

    info = clazz._split_info(src_dir_abs, dst_dir_abs, options)
    return info.items
  
  @classmethod
  def _existing_split_dirs(clazz, dst_dir, prefix):
    if not path.isdir(dst_dir):
      return []
    return dir_util.list_dirs(dst_dir, patterns = '*{}{}*'.format(path.sep, prefix))

  @classmethod
  def _existing_split_dirs_common_num_digits(clazz, dirs, prefix):
    basenames = [ path.basename(f) for f in dirs ]
    #clazz._log.log_d('basenames={}'.format(basenames))
    without_prefices = [ string_util.remove_head(f, prefix) for f in basenames ]
    #clazz._log.log_d('without_prefices={}'.format(without_prefices))
    lengths = list(set([ len(f) for f in without_prefices ]))
    if len(lengths) == 1:
      return lengths[0]
    return None

  @classmethod
  def _files_are_the_same(clazz, filename1, filename2):
    checksum1 = file_util.checksum('sha256', filename1)
    checksum2 = file_util.checksum('sha256', filename2)
    return checksum1 == checksum2

  @classmethod
  def _move_files(clazz, items, timestamp, count):
    for item in items:
      dst_filename = item.dst_filename
      if path.exists(item.dst_filename):
        if not clazz._files_are_the_same(item.src_filename, item.dst_filename):
          basename = path.basename(item.dst_filename)
          dirname = path.dirname(item.dst_filename)
          dst_basename = '{}-{}-{}'.format(timestamp, count, basename)
          dst_filename = path.join(dirname, dst_basename)
          count += 1
      file_util.rename(item.src_filename, dst_filename)

  @classmethod
  def _sort_file_info_list(clazz, file_info_list, order, reverse, partition):
    def _sort_key(finfo):
      criteria = []
      if partition:
        criteria.append(finfo.media_type)
      if order == dir_sort_order.FILENAME:
        criteria.append(finfo.filename)
      elif order == dir_sort_order.SIZE:
        criteria.append(file_util.size(finfo.filename))
      elif order == dir_sort_order.DATE:
        criteria.append(file_util.get_modification_date(finfo.filename))
      else:
        assert False
      return tuple(criteria)
    return sorted(file_info_list, key = _sort_key, reverse = reverse)

  @classmethod
  def _make_file_info_list(clazz, files, partition):
    result = []
    for filename in files:
      if partition:
        mime_type = file_attributes_metadata.get_mime_type(filename, fallback = True)
        media_type = file_mime.media_type_for_mime_type(mime_type)
      else:
        media_type = None
      result.append(clazz._file_info(filename, media_type))
    return result
  
  @classmethod
  def _partition_split_items(clazz, items):
    result = []
    dst_basename_map = clazz._make_dst_basename_map(items)
    for dst_basename, media_type_map in dst_basename_map.items():
      num_media_types = len(media_type_map)
      if num_media_types > 1:
        for media_type, items in media_type_map.items():
          for item in items:
            new_dst_filename = file_path.insert(item.dst_filename, -1, media_type)
            new_item = clazz._split_item(item.src_filename,
                                         new_dst_filename,
                                         item.chunk_number,
                                         item.dst_basename,
                                         item.media_type)
            result.append(new_item)
      else:
        for _, items in media_type_map.items():
          result.extend(items)

    return result

  @classmethod
  def _make_dst_basename_map(clazz, items):
    result_one = {}
    for item in items:
      if not item.dst_basename in result_one:
        result_one[item.dst_basename] = []
      result_one[item.dst_basename].append(item)
    result_two = {}
    for dst_basename, items in result_one.items():
      result_two[dst_basename] = clazz._make_media_type_map(items)
    return result_two
  
  @classmethod
  def _make_media_type_map(clazz, items):
    result = {}
    for item in items:
      if not item.media_type in result:
        result[item.media_type] = []
      result[item.media_type].append(item)
    return result
  
