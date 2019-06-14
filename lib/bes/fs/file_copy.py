#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os, shutil

from bes.system.host import host

from .tar_util import tar_util
from .file_util import file_util
from .dir_util import dir_util

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

  @classmethod
  def move_files(clazz, src_dir, dst_dir):
    if not path.isdir(src_dir):
      raise IOError('Not a directory: %s' % (src_dir))
    if not path.isdir(dst_dir):
      raise IOError('Not a directory: %s' % (dst_dir))
    if not file_util.same_device_id(src_dir, dst_dir):
      raise IOError('src_dir and dst_dir are not in the same device: %s %s' % (src, dst_dir))
    for f in dir_util.list(src_dir, relative = True):
      src_file = path.join(src_dir, f)
      dst_file = path.join(dst_dir, f)
      if path.isdir(src_file):
        if path.exists(dst_file):
          clazz.copy_tree(src_file, dst_file)
          file_util.remove(src_file)
        else:
          shutil.move(src_file, dst_file)
      else:
        os.rename(src_file, dst_file)
        
