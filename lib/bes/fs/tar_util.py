#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path, os, platform
from .file_util import file_util

class tar_util(object):

  def _find_tar_exe_tar():
    system = platform.system()
    if system == 'Linux':
      return '/bin/tar'
    elif system == 'Darwin':
      return '/usr/bin/tar'
    else:
      assert False, 'Dunno'

  TAR_EXE = _find_tar_exe_tar()
      
  @classmethod
  def copy_tree_with_tar(clazz, src_dir, dst_dir):
    if not path.isdir(src_dir):
      raise RuntimeError('src_dir is not a directory: %s' % (src_dir))
    file_util.mkdir(dst_dir)
    cmd = '%s -C %s -pcf - . | ( cd %s ; %s -pxf - )' % (clazz.TAR_EXE, src_dir, dst_dir, clazz.TAR_EXE)
    with os.popen(cmd) as pipe:
      pipe.read()
      pipe.close()
