#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import shutil

from bes.system.host import host

from .tar_util import tar_util
from .file_util import file_util

class file_copy(object):

  @classmethod
  def copy_tree(clazz, src_dir, dst_dir, excludes = None):
    'Copy src_dir to dst_dir recursively, preserving permissions and optionally excluding excludes.'
    if host.is_unix():
      tar_util.copy_tree(src_dir, dst_dir, excludes = excludes)
    else:
      clazz._copy_tree_windows(src_dir, dst_dir, excludes = excludes)
      
  @classmethod
  def _copy_tree_windows(clazz, src_dir, dst_dir, excludes = None):
    excludes = excludes or []
    shutil.copytree(src_dir, dst_dir, symlinks = True)
    for filename in excludes:
      p = path.join(dst_dir, filename)
      if path.exists(p):
        file_util.remove(p)
