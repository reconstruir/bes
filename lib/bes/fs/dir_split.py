#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.common.algorithm import algorithm
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.system.check import check
from bes.system.log import logger

from .dir_operation_item import dir_operation_item
from .dir_operation_item_type import dir_operation_item_type
from .dir_operation_item_list import dir_operation_item_list
from .dir_split_options import dir_split_options
from .dir_util import dir_util
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check
from .file_find import file_find
from .file_mime import file_mime
from .file_path import file_path
from .file_sort_order import file_sort_order
from .file_util import file_util
from .filename_list import filename_list

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
    info = clazz.split_info(src_dir_abs, dst_dir_abs, options)
    #assert len(info.items) > 0
    #for x in info.items:
    #  print(f'CACA: {x}')

    info.items.execute_operation(options.dup_file_timestamp,
                                 options.dup_file_count)

    #print(f'info.existing_split_dirs={info.existing_split_dirs}')
    for d in info.existing_split_dirs:
      if dir_util.is_empty(d):
        dir_util.remove(d)

    for next_possible_empty_root in info.possible_empty_dirs_roots:
      file_find.remove_empty_dirs(next_possible_empty_root)

    if path.exists(dst_dir_abs):
      file_find.remove_empty_dirs(dst_dir_abs)
      
  _split_items_info = namedtuple('_split_items_info', 'items, existing_split_dirs, possible_empty_dirs_roots')
  @classmethod
  def split_info(clazz, src_dir, dst_dir, options):
    assert path.isabs(src_dir)
    assert path.isabs(dst_dir)

    #print(f'src_dir={src_dir}')
    #print(f'dst_dir={dst_dir}')
    #for f in file_find.find(src_dir):
    #  print(f'SRC FILE: {f}')
    #for f in file_find.find(dst_dir):
    #  print(f'DST FILE: {f}')
    old_files = []
    existing_split_dirs = clazz._existing_split_dirs(dst_dir, options.prefix)
    #print(f'existing_split_dirs={existing_split_dirs}')
    for old_dir in existing_split_dirs:
      old_files.extend(dir_util.list_files(old_dir))
    clazz._log.log_d('old_files={}'.format(old_files))
    #print(f'old_files={old_files}')
    
    options = options or dir_split_options()
    items = dir_operation_item_list()
    if options.recursive:
      new_files = file_find.find(src_dir, relative = False, file_type = file_find.FILE)

      possible_empty_dirs_roots = []
      dirs = algorithm.unique([ path.dirname(f) for f in new_files ])
      for d in dirs:
        if d != src_dir:
          d_relative = file_util.remove_head(d, src_dir + path.sep)
          if not d_relative.startswith(options.prefix):
            d_root = path.join(src_dir, file_path.part(d_relative, 0))
            possible_empty_dirs_roots.append(d_root)
      possible_empty_dirs_roots = algorithm.unique(possible_empty_dirs_roots)
    else:
      new_files = dir_util.list_files(src_dir)
      possible_empty_dirs_roots = []

    for x in old_files:
      print(f'OLD: {x}')
    for x in new_files:
      print(f'NEW: {x}')
      
    files = algorithm.unique(old_files + new_files)
    sorted_files = clazz._sort_files(files,
                                     options.sort_order,
                                     options.sort_reverse)
    chunks = [ chunk for chunk in object_util.chunks(sorted_files, options.chunk_size) ]
    num_chunks = len(chunks)
    num_digits = len(str(num_chunks))
    for chunk_number, chunk in enumerate(chunks, start = 1):
      formatted_chunk_number = str(chunk_number).zfill(num_digits)
      dst_basename = f'{options.prefix}{formatted_chunk_number}'
      chunk_dst_dir = path.join(dst_dir, dst_basename)
      print(f'{chunk_number}: formatted_chunk_number={formatted_chunk_number}')
      print(f'{chunk_number}: dst_basename={dst_basename}')
      print(f'{chunk_number}: chunk_dst_dir={chunk_dst_dir}')
      for filename in chunk:
        dst_filename = path.join(chunk_dst_dir, path.basename(filename))
        #print(f'making item:\nfilename={filename}\ndst_filename={dst_filename}\ndst_basename={dst_basename}')
        item = dir_operation_item(filename, dst_filename, dir_operation_item_type.MOVE)
        items.append(item)
    return clazz._split_items_info(items, existing_split_dirs, possible_empty_dirs_roots)

  @classmethod
  def split_items(clazz, src_dir, dst_dir, options = None):
    'Return a list of split items that when renaming each item implements split.'
    src_dir_abs = file_check.check_dir(src_dir)
    check.check_string(dst_dir)
    dst_dir_abs = path.abspath(dst_dir)
    check.check_dir_split_options(options, allow_none = True)

    info = clazz.split_info(src_dir_abs, dst_dir_abs, options)
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
  def _sort_files(clazz, files, order, reverse):
    def _sort_key(filename):
      criteria = []
      if order == file_sort_order.FILENAME:
        criteria.append(filename)
      elif order == file_sort_order.SIZE:
        criteria.append(file_util.size(filename))
      elif order == file_sort_order.DATE:
        criteria.append(file_util.get_modification_date(filename))
      elif order == file_sort_order.DEPTH:
        criteria.append(file_path.depth(filename))
      else:
        assert False
      return tuple(criteria)
    return sorted(files, key = _sort_key, reverse = reverse)

  _MEDIA_TYPE_CACHE = {}
  @classmethod
  def _file_media_type(clazz, filename):
    assert path.isabs(filename)
    if not filename in clazz._MEDIA_TYPE_CACHE:
      mime_type = file_attributes_metadata.get_mime_type(filename, fallback = True)
      clazz._MEDIA_TYPE_CACHE[filename] = file_mime.media_type_for_mime_type(mime_type)
    return clazz._MEDIA_TYPE_CACHE[filename]
  
  @classmethod
  def _file_media_type(clazz, filename):
    mime_type = file_attributes_metadata.get_mime_type(filename, fallback = True)
    return file_mime.media_type_for_mime_type(mime_type)
