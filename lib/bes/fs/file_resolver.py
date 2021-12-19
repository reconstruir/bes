#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.common.algorithm import algorithm
from bes.system.check import check
from bes.common.object_util import object_util
from bes.system.log import logger

from .dir_util import dir_util
from .file_find import file_find
from .file_match import file_match
from .file_path import file_path
from .file_resolver_options import file_resolver_options
from .file_util import file_util
from .file_sort_order import file_sort_order

from .file_resolver_item import file_resolver_item
from .file_resolver_item_list import file_resolver_item_list

class file_resolver(object):

  _log = logger('file_resolver')
  
  @classmethod
  def resolve_files(clazz, files, options = None):
    'Resolve a mixed list of files and directories into a list of files.'
    check.check_file_resolver_options(options, allow_none = True)
    
    clazz._log.log_method_d()
    options = options or file_resolver_options()
    
    files = object_util.listify(files)
    result = file_resolver_item_list()
    index = 0
    for next_file in files:
      filename_abs = file_path.normalize(next_file)
      
      if not path.exists(filename_abs):
        raise IOError('File or directory not found: "{}"'.format(filename_abs))
      if path.isfile(filename_abs):
        filename = path.relpath(filename_abs)
        result.append(file_resolver_item(None, filename, filename_abs, index, index))
        index += 1
      elif path.isdir(filename_abs):
        next_entries = clazz._resolve_one_dir(filename_abs, options, index)
        index += len(next_entries)
        result.extend(next_entries)
    if options.sort_order:
      result = clazz._sort_result(result, options.sort_order, options.sort_reverse)
    if options.limit:
      result = result[0 : options.limit]
    return result

  @classmethod
  def _sort_result(clazz, result, order, reverse):
    assert order
    def _sort_key(resolved_file):
      criteria = []
      if order == file_sort_order.FILENAME:
        criteria.append(resolved_file.filename_abs)
      elif order == file_sort_order.SIZE:
        criteria.append(file_util.size(resolved_file.filename_abs))
      elif order == file_sort_order.DATE:
        criteria.append(file_util.get_modification_date(resolved_file.filename_abs))
      else:
        assert False
      return tuple(criteria)
    sorted_result = sorted(result, key = _sort_key, reverse = reverse)
    return clazz._reindex_result(sorted_result)

  @classmethod
  def _reindex_result(clazz, result):
    reindexed_result = file_resolver_item_list()
    for index, item in enumerate(result):
      reindexed_result.append(file_resolver_item(item.root_dir,
                                                 item.filename,
                                                 item.filename_abs,
                                                 index,
                                                 item.found_index))
    return reindexed_result
  
  @classmethod
  def _resolve_one_dir(clazz, root_dir, options, starting_index):
    result = []
    if options.recursive:
      max_depth = None
    else:
      max_depth = 1
    found_files = file_find.find(root_dir,
                                 relative = False,
                                 match_patterns = options.match_patterns,
                                 match_type = options.match_type,
                                 match_basename = options.match_basename,
                                 match_function = options.match_function,
                                 match_re = options.match_re,
                                 max_depth = max_depth)
    for index, next_filename in enumerate(found_files, start = starting_index):
      clazz._log.log_d('_resolve_one_dir:{}: next_filename={}'.format(index, next_filename))
      filename_abs = next_filename
      filename = path.relpath(filename_abs, start = root_dir)
      result.append(file_resolver_item(root_dir, filename, filename_abs, index, index))
    return result
