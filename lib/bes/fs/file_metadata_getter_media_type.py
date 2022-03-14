#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .file_metadata_getter_base import file_metadata_getter_base
from .file_check import file_check
from .file_mime import file_mime

class file_metadata_getter_media_type(file_metadata_getter_base):

  @classmethod
  #@abstractmethod
  def name(self):
    'Return the name of this getter.'
    return 'media_type'
  
  #@abstractmethod
  def get_value(self, manager, filename):
    'Get a metadata value from filename and return it encoded as bytes.'
    file_check.check_file(filename)

    mime_type = manager.get_mime_type(filename, fallback = True, cached = True)
    return file_mime.media_type_for_mime_type(mime_type).encode('utf-8')

  #@abstractmethod
  def decode_value(self, value):
    'Decode a value given as bytes.'
    check.check_bytes(value)

    return value.decode('utf-8')
