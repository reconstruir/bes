#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from collections import namedtuple

from bes.common.algorithm import algorithm
from bes.common.object_util import object_util
from bes.fs.file_find import file_find
from bes.fs.file_match import file_match

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
      result.append(clazz.resolved_file(d, f, path.join(d, f)))
    return result
