#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .file_metadata_getter_base import file_metadata_getter_base
from .file_check import file_check
from .file_util import file_util

class file_metadata_getter_checksum_sha256(file_metadata_getter_base):

  @classmethod
  #@abstractmethod
  def name(self):
    'Return the name of this getter.'
    return 'checksum_sha256'
  
  #@abstractmethod
  def get_value(self, manager, filename):
    'Get a metadata value from filename and return it encoded as bytes.'
    file_check.check_file(filename)

    return file_util.checksum('sha256', filename).encode('utf-8')

  #@abstractmethod
  def decode_value(self, value):
    'Decode a value given as bytes.'
    check.check_bytes(value)

    return value.decode('utf-8')
