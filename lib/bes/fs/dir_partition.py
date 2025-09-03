#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.system.check import check
from bes.system.log import logger
from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options

from .dir_operation_item import dir_operation_item
from .dir_operation_item_list import dir_operation_item_list
from .dir_partition_criteria_media_type import dir_partition_criteria_media_type
from .dir_partition_criteria_prefix import dir_partition_criteria_prefix
from .dir_partition_options import dir_partition_options
from .dir_partition_type import dir_partition_type
from .file_check import file_check
from .file_find import file_find
from bes.files.bf_path import bf_path
from .file_util import file_util
from .filename_list import filename_list

class dir_partition(object):
  'A class to partition directories'

  _log = logger('dir_partition')

  @classmethod
  def partition(clazz, files, options = None):
    check.check_string_seq(files)
    check.check_dir_partition_options(options, allow_none = True)

    options = options or dir_partition_options()
    
    info = clazz.partition_info(files, options = options)
    info.items.move_files(options.dup_file_timestamp,
                          options.dup_file_count)
    if options.delete_empty_dirs:
      clazz._log.log_d(f'resolved_files={info.resolved_files}')
      root_dirs = info.resolved_files.root_dirs()
      clazz._log.log_d(f'root_dirs={root_dirs}')
      for next_possible_empty_root in root_dirs:
        file_find.remove_empty_dirs(next_possible_empty_root)
    return info
      
  _partition_info_result = namedtuple('_partition_items_info', 'items, resolved_files')
  @classmethod
  def partition_info(clazz, files, options = None):
    check.check_string_seq(files)
    check.check_dir_partition_options(options, allow_none = True)

    dst_dir_abs = path.abspath(options.dst_dir)
    options = options or dir_partition_options()

    clazz._log.log_d(f'options={options}')

    if options.partition_type == None:
      return items
    elif options.partition_type == dir_partition_type.MEDIA_TYPE:
      criteria = dir_partition_criteria_media_type()
      result = clazz._partition_info_by_criteria(files, dst_dir_abs, criteria, options)
    elif options.partition_type == dir_partition_type.PREFIX:
      criteria = dir_partition_criteria_prefix()
      result = clazz._partition_info_by_criteria(files, dst_dir_abs, criteria, options)
    elif options.partition_type == dir_partition_type.CRITERIA:
      result = clazz._partition_info_by_criteria(files, dst_dir_abs, options.partition_criteria, options)
    else:
      raise RuntimeError(f'Unkown partition type: {options.partition_type}')
    return result
  
  @classmethod
  def _resolve_files(clazz, files, recursive):
    resolver_options = file_resolver_options(sort_order = 'depth',
                                             sort_reverse = True,
                                             recursive = recursive)
    return file_resolver.resolve_files(files, options = resolver_options)

  @classmethod
  def _partition_info_by_criteria(clazz, files, dst_dir_abs, criteria, options):
    if not criteria:
      raise RuntimeError('No partition_criteria given for partition_type "criteria"')
    resolved_files = clazz._resolve_files(files, options.recursive)
    for f in resolved_files:
      clazz._log.log_d(f'resolved_file: {f.root_dir} - {f.filename}')

    classifications = {}
    for f in resolved_files:
      classification = criteria.classify(f.filename_abs)
      if classification != None:
        if not check.is_string(classification):
          raise TypeError(f'Classify should return a string: {criteria}')
        if not classification in classifications:
          classifications[classification] = dir_operation_item_list()
        if options.flatten:
          dst_basename = path.basename(f.filename_abs)
        else:
          dst_basename = f.filename
        dst_filename = path.join(dst_dir_abs, classification, dst_basename)
        item = dir_operation_item(f.filename_abs, dst_filename)
        classifications[classification].append(item)

    items = dir_operation_item_list()
    for classification, classification_items in classifications.items():
      num_files = len(classification_items)
      threshold_met = options.threshold == None or num_files >= options.threshold
      clazz._log.log_d(f'classification={classification} num_files={num_files} threshold_met={threshold_met}')
      if threshold_met:
        items.extend(classification_items)
    items.sort(key = lambda item: item.src_filename)
    return clazz._partition_info_result(items, resolved_files)
