#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os, tarfile
from bes.system import execute, host

from .file_util import file_util
from .temp_file import temp_file

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
  def extract(clazz, filename, dest_dir):
    execute.execute('tar xf {filename} -C {dest_dir}'.format(filename = filename, dest_dir = dest_dir))

  @classmethod
  def supported_formats(clazz):
    'Return a list of names of the formats the tar command line util supports'
    tmp_dir = temp_file.make_temp_dir()
    file_util.save(path.join(tmp_dir, 'x.txt', content = 'x'))
    cmd = 'tar Jcf foo.tar -C %s x.txt' % (tmp_dir)
    rv = execute.execute(cmd, cwd = tmp_dir, raise_error = False)
    
