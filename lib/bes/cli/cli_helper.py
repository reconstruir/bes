#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from os import path
import inspect
from bes.system.log import logger

from bes.common.check import check
from bes.common.object_util import object_util
from bes.system.log import log
from bes.fs.file_check import file_check
from bes.fs.file_find import file_find
#from bes.git.git import git

class cli_helper(object):
  'A class to help implement clis'

#####  @classmethod
#####  def check_file(clazz, filename):
#####    file_check.check_file(filename)
#####
#####  @classmethod
#####  def check_dir(clazz, dirname):
#####    file_check.check_dir(dirname)
#####
#####  @classmethod
#####  def check_dir_is_git_repo(clazz, d):
#####    git.check_is_git_repo(d)
#####
#####  @classmethod
#####  def resolve_file(clazz, filename, root_dir = None):
#####    '''
#####    Resolve a filename as follows:
#####     . expand ~ to $HOME
#####     . make it an absolute path
#####    '''
#####    if root_dir:
#####      filename = path.join(root_dir, filename)
#####    else:
#####      if '~' in filename:
#####        filename = path.expanduser(filename)
#####      if not path.isabs(filename):
#####        filename = path.abspath(filename)
#####    return filename
#####
#####  @classmethod
#####  def resolve_dir(clazz, dirname, root_dir = None):
#####    return clazz.resolve_file(dirname, root_dir = root_dir)

  @classmethod
  def resolve_files(clazz, what, func = None):
    '''
    Return a list of absolute filenames for what.
    'what' can be one or more of:
    - a file
    - a directory to search for files
    '''
    check.check_function(func, allow_none = True)
    if not what:
      return []
    what = object_util.listify(what)
    result = []
    for x in what:
      result.extend(clazz._resolve_one(x))
    result = sorted(list(set(result)))
    if func:
      result = [ f for f in result if func(f) ]
    return result
      
  @classmethod
  def _resolve_one(clazz, filename):
    filename = path.abspath(filename)
    if path.isfile(filename):
      return [ filename ]
    elif path.isdir(filename):
      return file_find.find(filename, relative = False, file_type = file_find.FILE)
    if path.exists(filename):
      raise RuntimeError('File not a file or dir: {}'.format(filename))
    raise RuntimeError('File not found: {}'.format(filename))
