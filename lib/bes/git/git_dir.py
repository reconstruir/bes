#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import os
import os.path as path
#import copy
#from collections import namedtuple
#
#from bes.common.check import check
#from bes.common.string_util import string_util
from bes.common.object_util import object_util
#from bes.fs.file_type import file_type
from bes.fs.file_util import file_util
from bes.fs.find.criteria import criteria
#from bes.fs.find.file_type_criteria import file_type_criteria
from bes.fs.find.finder import finder
#from bes.fs.find.max_depth_criteria import max_depth_criteria
from bes.fs.find.pattern_criteria import pattern_criteria
#from bes.fs.temp_file import temp_file
#from bes.system.execute import execute
#from bes.system.log import logger
#from bes.script.blurber import blurber
#
#from .git import git
#from .git_repo import git_repo
#from .git_commit_info import git_commit_info
#from .git_repo_script_options import git_repo_script_options
#from .git_repo_operation_options import git_repo_operation_options

from bes.system.log import logger

class git_dir(object):
  'Class to deal with groups of git directories.'

  _log = logger('git')

  @classmethod
  def find_git_dirs(clazz, dirs):
    'Return the first .git dir found in any dir in dirs.'
    dirs = object_util.listify(dirs)
    dirs = [ d for d in dirs if path.isdir(d) ]
    possible = []
    result = clazz._find(dirs, '.git', None, None, False)
    result = [ file_util.remove_tail(d, '.git') for d in result ]
    return sorted(result)

  @classmethod
  def _find(clazz, files, name, ft, max_depth, quit):
    if ft:
      ft = file_type.validate_file_type(ft)
    for f in files:
      if path.isdir(f):
        ff = clazz._make_finder(f, name, ft, max_depth, quit)
        for f in ff.find():
          yield f

  @classmethod
  def _make_finder(clazz, d, name, ft, max_depth, quit):
    crit_list = []
    if max_depth:
      crit_list.append(max_depth_criteria(max_depth))
    if name:
      if quit:
        action = criteria.STOP
      else:
        action = criteria.FILTER
      crit_list.append(pattern_criteria(name, action = action))
    if ft:
      crit_list.append(file_type_criteria(ft))
    return finder(d, criteria = crit_list)

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
  
