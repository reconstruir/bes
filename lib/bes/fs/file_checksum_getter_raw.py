#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.bf_file_ops import bf_file_ops
from bes.files.checksum.bf_checksum import bf_checksum
from .file_checksum_getter_base import file_checksum_getter_base

class file_checksum_getter_raw(file_checksum_getter_base):

  #@abstractmethod
  def checksum(self, algorithm, filename):
    'Return the checksum for filename using algorithm.'
    return bf_checksum.checksum(filename, algorithm)
