#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system.log import logger

class git_dir(object):
  'Class to deal with groups of git directories.'

  _log = logger('git')

  @classmethod
  def find_git_dirs(clazz, dirs):
    'Return the first .git dir found in any dir in dirs.'
    from .git_util import git_util
    return git_util.find_git_dirs(dirs)

  @classmethod
  def _resolve_git_dirs(clazz, dirs, excludes = None, includes = None):
    git_dirs = clazz.find_git_dirs(dirs)
    git_dirs = clazz._filter_git_dirs(git_dirs, excludes, includes)
    return clazz._ignore_git_dirs(git_dirs)

  @classmethod
  def _filter_git_dirs(clazz, dirs, excludes, includes):
    dirs2 = clazz._filter_git_dirs_excludes(dirs, excludes)
    return clazz._filter_git_dirs_includes(dirs2, includes)

  @classmethod
  def _filter_git_dirs_excludes(clazz, dirs, excludes):
    if not excludes:
      return dirs
    result = []
    for i in excludes:
      for d in dirs:
        if i not in d:
          result.append(d)
    return result

  @classmethod
  def _filter_git_dirs_includes(clazz, dirs, includes):
    if not includes:
      return dirs
    result = []
    for d in dirs:
      if clazz._dir_matches_includes(d, includes):
        result.append(d)
    return result

  @classmethod
  def _dir_matches_includes(clazz, d, includes):
    for i in includes:
      if i in d:
        return True
    return False
  
  @classmethod
  def _ignore_git_dirs(clazz, dirs):
    git_dirs = [ d for d in dirs if 'BUILD/' not in d ]
    git_dirs = [ d for d in git_dirs if '.ego_build_list_tmp' not in d ]
    git_dirs = [ d for d in git_dirs if path.isdir(d) ]
    return git_dirs
  
