#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

class bf_metadata_database_locator:

  DEFAULT_DATABASE_PATH = '~/.bes/metadata/metadata.db'

  @classmethod
  def default_database_path(clazz):
    return path.expanduser(clazz.DEFAULT_DATABASE_PATH)
