#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.common.algorithm import algorithm
from bes.common.object_util import object_util
from bes.fs.dir_util import dir_util
from bes.fs.file_find import file_find
from bes.fs.file_match import file_match
from bes.fs.file_util import file_util

class file_resolve(object):

  resolved_file = namedtuple('resolved_file', 'where, filename, filename_abs')
  
  @classmethod
  def filepath_normalize(clazz, filepath):
    return path.abspath(path.normpath(filepath))

  @classmethod
  def filepaths_normalize(clazz, files):
    return [ clazz.filepath_normalize(f) for f in files ]

  @classmethod
  def resolve_files(clazz, files, patterns = None, exclude_patterns = None):
    'Resolve a mixed list of files and directories into a sorted list of files.'
    files = object_util.listify(files)
    result = []
    for f in files:
      if not path.exists(f):
        raise RuntimeError('Not found: %s' % (f))
      if path.isfile(f):
        result.append(clazz.filepath_normalize(f))
      elif path.isdir(f):
        result += file_find.find_fnmatch(f, patterns, relative = False)
      result = sorted(algorithm.unique(result))
      if not exclude_patterns:
        return result
      return file_match.match_fnmatch(result, exclude_patterns, file_match.NONE)

  @classmethod
  def resolve_dir(clazz, d, patterns = None, match_type = None):
    d = path.normpath(d)
    files = file_find.find(d, file_type = file_find.FILE, relative = True,
                           match_patterns = patterns, match_type = match_type)
    result = []
    for f in files:
      fabs = path.join(d, f)
      result.append(clazz.resolved_file(d, f, fabs))
    return sorted(result)

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
    base_dir_basename = file_util.remove_head(rf.where, base_dir)
    where = rf.where
    filename = path.join(base_dir_basename, rf.filename)
    filename_abs = path.join(rf.where, filename)
    return clazz.resolved_file(where, filename, filename_abs)
