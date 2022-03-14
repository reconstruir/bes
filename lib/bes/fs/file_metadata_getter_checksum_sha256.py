#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .file_metadata_getter_base import file_metadata_getter_base
from .file_util import file_util

class file_metadata_getter_checksum_sha_256(file_metadata_getter_base):

  #@abstractmethod
  def name(self):
    'Return the name of this getter.'
    return 'checksum_sha_256'
  
  #@abstractmethod
  def key_name(self):
    'Return the key name.'
    return 'bes_checksum_sha256'
  
  #@abstractmethod
  def get_value(self, filename):
    'Get the metadata value from filename.'
    return file_util.checksum('sha256', filename).encode('utf-8')
