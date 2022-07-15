#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from .file_checksum_db import file_checksum_db
from .file_checksum_getter_base import file_checksum_getter_base

class file_checksum_getter_db(file_checksum_getter_base):

  def __init__(self, db_filename):
    self._db = file_checksum_db(path.dirname(db_filename),
                                db_filename = path.basename(db_filename))
  
  #@abstractmethod
  def checksum(self, algorithm, filename):
    'Return the checksum for filename using algorithm.'
    return self._db.checksum(algorithm, filename)
