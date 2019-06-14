#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import shutil

from bes.system.host import host

from .tar_util import tar_util

class file_copy(object):

  @classmethod
  def copy_tree(clazz, src_dir, dst_dir, excludes = None):
    'Copy src_dir to dst_dir recursively, preserving permissions and optionally excluding excludes.'
#    shutil.copytree(src_dir, dst_dir, symlinks = True)
#    return
    if host.is_unix():
      return tar_util.copy_tree(src_dir, dst_dir, excludes = excludes)
    else:
      assert False
