#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from bes.common.check import check
from bes.property.cached_property import cached_property
from bes.fs.file_util import file_util
from bes.fs.file_symlink import file_symlink
from bes.git.git import git
from bes.git.git_error import git_error

class file_info(namedtuple('file_info', 'filename, config, inspection')):

  def __new__(clazz, config_env, filename, inspection):
    if filename is not None:
      check.check_string(filename)
    if not path.isfile(filename):
      raise IOError('File not found: %s' % (filename))
    filename = path.abspath(filename)
    config = config_env.config_for_filename(filename)
    return clazz.__bases__[0].__new__(clazz, filename, config, inspection)

  @cached_property
  def relative_filename(self):
    'Return the filename relative to the config root_dir or None if no config was found.'
    if self.config:
      return file_util.remove_head(self.filename, self.config.root_dir)
    else:
      return None

  @cached_property
  def git_root(self):
    'Return the git root for this file or None if not within a git repo.'
    try:
      return git.root(self.filename)
    except git_error as ex:
      return None
    except Exception as ex:
      raise
    
  @cached_property
  def git_tracked(self):
    'Return True if the file is tracked by the git repo.'
    if not self.git_root:
      return False
    return git.is_tracked(self.git_root, self.filename)

  @property
  def is_broken_link(self):
    return file_symlink.is_broken(self.filename)

check.register_class(file_info, include_seq = False)
