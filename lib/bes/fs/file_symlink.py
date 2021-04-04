#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.system.host import host

from .file_util import file_util

class file_symlink(object):
  'Class to deal with symlinks.'

  @classmethod
  def has_support(clazz):
    'Return True if the current system has support and priviledges for symlinks.'
    if host.is_unix():
      return True
    elif host.is_windows():
      from .detail.file_symlink_windows import file_symlink_windows
      return file_symlink_windows.enable_symlink_privilege()
    else:
      raise RuntimeError('unsupported system: %s' % (host.SYSTEM))
  
  @classmethod
  def symlink(clazz, src, dst):
    file_util.remove(dst)
    os.symlink(src, dst)

  @classmethod
  def is_broken(clazz, filename):
    return path.islink(filename) and not path.exists(os.readlink(filename))

  @classmethod
  def resolve(clazz, filename):
    if not path.islink(filename):
      return path.normpath(filename)

    seen = set()
    next_filename = filename
    while True:
      if next_filename in seen:
        raise IOError('Cyclic error in symlink "{}": "{}"'.format(filename,
                                                                  next_filename))
      seen.add(next_filename)
      if not path.islink(next_filename):
        break
      next_filename = clazz._resolve_symlink(next_filename)
    return next_filename

  @classmethod
  def _resolve_symlink(clazz, link):
    assert path.islink(link)
    target = os.readlink(link)
    if path.isabs(target):
      result = target
    else:
      result = path.join(path.dirname(link), target)
    return path.normpath(result)
