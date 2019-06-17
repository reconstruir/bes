#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os

from .file_util import file_util

class file_symlink(object):
  'Class to deal with symlinks.'
  
  @classmethod
  def symlink(clazz, src, dst):
    file_util.remove(dst)
    os.symlink(src, dst)

  @classmethod
  def is_broken(clazz, filename):
    return path.islink(filename) and not path.exists(os.readlink(filename))
