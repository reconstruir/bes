#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .file_checksum_db import file_checksum_db
from .file_checksum_getter import file_checksum_getter

class file_checksum_getter_db(file_checksum_getter):

  def __init__(self, db_filename):
    self._db = file_checksum_db(db_filename)
  
  #@abstractmethod
  def checksum(self, algorithm, filename):
    'Return the checksum for filename using algorithm.'
    return self._db.checksum(algorithm, filename)
