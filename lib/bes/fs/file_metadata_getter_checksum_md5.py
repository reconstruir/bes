#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .file_metadata_getter_checksum import file_metadata_getter_checksum

class file_metadata_getter_checksum_md5(file_metadata_getter_checksum):

  def __init__(self):
    super().__init__('md5')

  @classmethod
  #@abstractmethod
  def name(self):
    'Return the name of this getter.'
    return 'bes_checksum_md5'
