#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

class bf_file_mover_database_locator:
  'Suggests a conventional path for the mover database. The caller is free to use any path.'

  @classmethod
  def default_database_path(clazz):
    'Return the default database path: ~/.bes/move/move.sqlite'
    return path.expanduser(path.join('~', '.bes', 'move', 'move.sqlite'))
