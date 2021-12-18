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

class file_resolver(object):

  _resolved_file = namedtuple('_resolved_file', 'root_dir, filename, filename_abs, index')

  _log = logger('file_resolver')
  
  @classmethod
  def resolve_files(clazz,
                    files,
                    options = None,
                    match_patterns = None,
                    match_type = None,
                    match_basename = True,
                    match_function = None,
                    match_re = None):
    'Resolve a mixed list of files and directories into a list of files.'
    check.check_file_resolver_options(options, allow_none = True)
    
    clazz._log.log_method_d()
    options = options or file_resolver_options()
    
    files = object_util.listify(files)
    result = []
    index = 0
    for next_file in files:
      filename_abs = file_path.normalize(next_file)
      
      if not path.exists(filename_abs):
        raise IOError('File or directory not found: "{}"'.format(filename_abs))
      if path.isfile(filename_abs):
        filename = path.relpath(filename_abs)
        result.append(clazz._resolved_file(None, filename, filename_abs, index))
        index += 1
      elif path.isdir(filename_abs):
        next_entries = clazz._resolve_one_dir(filename_abs,
                                              options,
                                              index,
                                              match_patterns,
                                              match_type,
                                              match_basename,
                                              match_function,
                                              match_re)
        index += len(next_entries)
        result.extend(next_entries)
    if options.sort_order:
      result = _clazz._sort_result(result, options.sort_order, options.sort_reverse)
    if options.limit:
      result = result[0 : options.limit]
    return result

  @classmethod
  def _sort_result(clazz, result, order, reverse):
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
    return sorted(result, key = _sort_key, reverse = reverse)
  
  @classmethod
  def _resolve_one_dir(clazz, root_dir, options, starting_order,
                       match_patterns, match_type, match_basename,
                       match_function, match_re):
    result = []
    if options.recursive:
      max_depth = None
    else:
      max_depth = 1
    found_files = file_find.find(root_dir,
                                 relative = True,
                                 match_patterns = match_patterns,
                                 match_type = match_type,
                                 match_basename = match_basename,
                                 match_function = match_function,
                                 match_re = match_re,
                                 max_depth = max_depth)
    for order, next_filename in enumerate(found_files, start = starting_order):
      clazz._log.log_d('_resolve_one_dir:{}: next_filename={}'.format(order, next_filename))
      filename_abs = path.join(root_dir, next_filename)
      filename = path.relpath(filename_abs, start = root_dir)
      result.append(clazz._resolved_file(root_dir, filename, filename_abs, order))
    return result
    
  @classmethod
  def resolve_dir(clazz, d, patterns = None, match_type = None):
    d = path.normpath(d)
    files = file_find.find(d, file_type = file_find.FILE, relative = True,
                           match_patterns = patterns, match_type = match_type)
    result = []
    for order, f in enumerate(files):
      fabs = path.join(d, f)
      result.append(clazz.resolved_file(d, f, fabs, order))
    return sorted(result, key = lambda f: f.filename_abs)

  @classmethod
  def resolve_mixed(clazz, base_dir, files_or_dirs, patterns = None, match_type = None):
    files_or_dirs = object_util.listify(files_or_dirs)

    if not files_or_dirs:
      files_or_dirs = dir_util.list(base_dir, relative = True)

    result = []
    for f in files_or_dirs:
      if path.isabs(f):
        frel = file_util.remove_head(f, base_dir)
        fabs = f
      else:
        frel = f
        fabs = path.join(base_dir, f)
      if not path.exists(fabs):
        raise IOError('File or directory not found: "{}"'.format(fabs))
      if path.isfile(fabs):
        include = True
        if patterns:
          include = file_match.match_fnmatch(f, patterns, match_type = match_type)
        if include:
          result.append(clazz.resolved_file(base_dir, frel, fabs))
      elif path.isdir(fabs):
        next_result = clazz.resolve_dir(fabs, patterns = patterns, match_type = match_type)
        next_result = [ clazz._fix_resolved_file_filenames(rf, base_dir) for rf in next_result ]
        result += next_result
    return sorted(algorithm.unique(result))

  @classmethod
  def _fix_resolved_file_filenames(clazz, rf, base_dir):
    base_dir_basename = file_util.remove_head(rf.root_dir, base_dir)
    root_dir = base_dir
    filename = path.join(base_dir_basename, rf.filename)
    filename_abs = path.join(root_dir, filename)
    return clazz.resolved_file(root_dir, filename, filename_abs)
