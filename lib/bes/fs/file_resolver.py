#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from collections import namedtuple

from bes.common.algorithm import algorithm
from bes.system.check import check
from bes.common.object_util import object_util
from bes.system.log import logger

from .dir_util import dir_util
from .file_check import file_check
from .file_find import file_find
from .file_match import file_match
from .file_path import file_path
from .file_resolver_options import file_resolver_options
from .file_sort_order import file_sort_order
from .file_util import file_util
from .filename_list import filename_list

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
    return clazz._do_resolve_files(files, options, file_find.FILE)

  @classmethod
  def resolve_dirs(clazz, dirs, options = None):
    'Resolve a directories only.'
    check.check_file_resolver_options(options, allow_none = True)
    
    clazz._log.log_method_d()

    dirs = object_util.listify(dirs)
    file_check.check_dir_seq(dirs)
    options = options or file_resolver_options()
    return clazz._do_resolve_files(dirs, options, file_find.DIR)
  
  @classmethod
  def _do_resolve_files(clazz, files, options, file_type):
    'Resolve a mixed list of files and directories into a list of files.'

    clazz._log.log_d(f'_do_resolve_files(files={files} file_type={file_type}')
    
    found_files, root_dir = clazz._find_files(files, options, file_type)
    clazz._log.log_d(f'_do_resolve_files: found_files={found_files} root_dir={root_dir}')
    result = file_resolver_item_list()
    index = 0
    for filename_abs in found_files:
      filename_rel = path.relpath(filename_abs, start = root_dir)
      if not options.should_ignore_file(filename_abs):
        item = file_resolver_item(root_dir, filename_rel, filename_abs, index, index)
        result.append(item)
        index = index + 1

    if options.sort_order:
      result = clazz._sort_result(result, options.sort_order, options.sort_reverse)
    if options.limit:
      result = result[0 : options.limit]
    return result

  _resolved_item = namedtuple('_resolved_item', 'filename_abs, root_dir')
  @classmethod
  def _find_files(clazz, files, options, file_type):
    'Resolve a mixed list of files and directories into a list of files.'

    files = object_util.listify(files)
    items = []
    for i, f in enumerate(files, start = 1):
      clazz._log.log_d(f'_find_files: files: {i}: {f}')
    for next_file in files:
      filename_abs = file_path.normalize(next_file)
      if not path.exists(filename_abs):
        raise IOError('File or directory not found: "{}"'.format(filename_abs))
      if path.isfile(filename_abs):
        item = clazz._resolved_item(filename_abs, path.dirname(filename_abs))
        items.append(item)
      elif path.isdir(filename_abs):
        next_entries = clazz._find_files_in_dir(filename_abs, options, 0, file_type)
        for next_entry in next_entries:
          item = clazz._resolved_item(next_entry, next_file)
          items.append(item)
    found_files = [ item.filename_abs for item in items ]
    for i, f in enumerate(found_files, start = 1):
      clazz._log.log_d(f'_find_files: found_files: {i}: {f}')
    if len(found_files) == 1:
      root_dir = items[0].root_dir
      clazz._log.log_d(f'_find_files: one file: root_dir={root_dir}')
    else:
      filenames = [ item.filename_abs for item in items ]
      root_dir = None
      # FIXME: instead of checking for one file, we need to figure out
      # dirs in files and then calssify all the found files according
      # to that prefix
      if len(files) == 1:
        if filename_list.startswith(filenames, files[0]):
          root_dir = files[0]
      if not root_dir:
        root_dir = file_path.common_ancestor(filenames)
      assert root_dir
      clazz._log.log_d(f'_find_files: many files: root_dir={root_dir}')
    return found_files, root_dir
  
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
      elif order == file_sort_order.DEPTH:
        criteria.append(file_path.depth(resolved_file.filename_abs))
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
  def _find_files_in_dir(clazz, root_dir, options, starting_index, file_type):
    result = []
    if options.recursive:
      max_depth = None
    else:
      max_depth = 1
    found_files = file_find.find(root_dir,
                                 relative = False,
                                 file_type = file_type,
                                 match_patterns = options.match_patterns,
                                 match_type = options.match_type,
                                 match_basename = options.match_basename,
                                 match_function = options.match_function,
                                 match_re = options.match_re,
                                 max_depth = max_depth)
    return found_files

  @classmethod
  def resolve_empty_dirs(clazz, dirs, recursive = False):
    'Resolve empty dirs.'
    
    def _match_empty_dirs(d):
      assert path.isdir(d)
      return dir_util.is_empty(d)
    
    options = file_resolver_options(recursive = recursive,
                                    match_function = _match_empty_dirs,
                                    match_basename = False)
    return file_resolver.resolve_dirs(dirs, options = options)
