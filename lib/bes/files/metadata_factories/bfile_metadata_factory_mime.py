#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_checksum import bfile_checksum
from ..mime.bfile_mime import bfile_mime

from ..metadata.bfile_metadata_factory_base import bfile_metadata_factory_base

class bfile_metadata_factory_mime(bfile_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      ( 'bes/mime/mime_type/1.0', lambda f: bfile_mime.mime_type(f), clazz.decode_string, clazz.encode_string, check.check_string ),
      ( 'bes/mime/media_type/1.0', lambda f: clazz._media_type_1_0(f), clazz.decode_string, clazz.encode_string, check.check_string ),
    ]
  
  @classmethod
  def _media_type_1_0(clazz, filename):
    mime_type = clazz.metadata_class.get_metadata(filename, 'bes/mime/mime_type/1.0')
    media_type = bfile_mime.media_type_for_mime_type(mime_type)
    if media_type == None:
      media_type = 'unknown'
    return media_type
