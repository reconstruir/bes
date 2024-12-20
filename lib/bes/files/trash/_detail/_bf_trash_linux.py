#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.files.bf_dir import bf_dir
from bes.system.filesystem import filesystem
from bes.system.log import logger

from ._bf_trash_i import _bf_trash_i

class _bf_trash_linux(_bf_trash_i):
  
  @classmethod
  #@abstractmethod
  def empty_trash(clazz):
    'Empty the trash.'
    trash_root = path.expanduser('~/.local/share/Trash')
    trash_dirs = [ path.join(trash_root, d) for d in ( 'files', 'info' ) ]
    for next_trash_dir in trash_dirs:
      trash_files = bf_dir.list(next_trash_dir)
      filesystem.remove(trash_files)
