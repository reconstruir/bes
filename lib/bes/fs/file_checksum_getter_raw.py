#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .file_util import file_util
from .file_checksum_getter_base import file_checksum_getter_base

class file_checksum_getter_raw(file_checksum_getter_base):

  #@abstractmethod
  def checksum(self, algorithm, filename):
    'Return the checksum for filename using algorithm.'
    return file_util.checksum(algorithm, filename)
