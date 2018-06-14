#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os, tarfile
from bes.system import execute, host

from .file_util import file_util

class tar_util(object):

  def _find_tar_exe_tar():
    'Find the tar executable explicitly in the system default place in case the user aliased it somehow'
    if host.is_linux():
      return '/bin/tar'
    elif host.is_macos():
      return '/usr/bin/tar'
    else:
      raise RuntimeError('Unknown host system')

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

  @classmethod
  def members(clazz, filename):
    cmd = 'tar tf %s' % (filename)
    rv = execute.execute(cmd)
    return [ i for i in rv.stdout.split('\n') if i ]

  @classmethod
  def has_member(clazz, filename, member):
    'Return True if filename is in the tar members.'
    with tarfile.open(filename, mode = 'r') as archive:
      try:
        archive.getmember(member)
        return True
      except KeyError as ex:
        pass
      return False
