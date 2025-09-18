#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from bes.system.filesystem import filesystem

from .bf_error import bf_error

class bf_symlink(object):
  'Class to deal with symlinks.'

  @classmethod
  def has_support(clazz):
    'Return True if the current system has support and priviledges for symlinks.'
    return filesystem.has_symlinks()
  
  @classmethod
  def symlink(clazz, src, dst):
    filesystem.remove(dst)
    os.symlink(src, dst)

  @classmethod
  def is_broken(clazz, filename):
    if not path.islink(filename):
      return False
    resolved_link = clazz._resolve_symlink(filename)
    return not path.exists(resolved_link)

  @classmethod
  def resolve(clazz, filename):
    if not path.islink(filename):
      return path.normpath(filename)

    seen = set()
    next_filename = filename
    while True:
      if next_filename in seen:
        raise bf_error(f'Cyclic error in symlink "{filename}": "{next_filename}"')
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
