#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .file_metadata_getter_base import file_metadata_getter_base

from bes.files.bf_check import bf_check
from bes.files.checksum.bf_checksum_cache import bf_checksum_cache

class file_metadata_getter_checksum(file_metadata_getter_base):

  def __init__(self, algorithm):
    check.check_string(algorithm)

    assert algorithm in ( 'sha1', 'sha256', 'md5' )
    self._algorithm = algorithm
  
  #@abstractmethod
  def get_value(self, manager, filename):
    'Get a metadata value from filename and return it encoded as bytes.'
    bf_check.check_file(filename)

    return bf_checksum_cache.get_checksum(filename, self._algorithm).encode('utf-8')

  #@abstractmethod
  def decode_value(self, value):
    'Decode a value given as bytes.'
    check.check_bytes(value)

    return value.decode('utf-8')
