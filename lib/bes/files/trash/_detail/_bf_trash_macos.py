#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.files.bf_dir import bf_dir
from bes.system.filesystem import filesystem
from bes.system.log import logger

from ._bf_trash_i import _bf_trash_i

class _bf_trash_macos(_bf_trash_i):

  _log = logger('bf_trash')

  @classmethod
  #@abstractmethod
  def empty_trash(clazz):
    'Empty the trash.'
    trash_root = path.expanduser('~/.Trash')
    trash_files = bf_dir.list(trash_root)
    filesystem.remove(trash_files)
