#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bf_checksum import bf_checksum
from ..mime.bf_mime import bf_mime

from ..metadata.bf_metadata_factory_base import bf_metadata_factory_base

class bf_metadata_factory_mime(bf_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      (
        'bes/mime/mime_type/1.0',
        lambda f: bf_mime.mime_type(f),
        clazz.encoding.decode_string,
        clazz.encoding.encode_string,
        check.check_string,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_mime_type')
      ),
      (
        'bes/mime/media_type/1.0',
        lambda f: clazz._media_type_1_0(f),
        clazz.encoding.decode_string,
        clazz.encoding.encode_string,
        check.check_string,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_media_type')
      )
    ]
  
  @classmethod
  def _media_type_1_0(clazz, filename):
    mime_type = clazz.metadata.get_metadata(filename, 'bes/mime/mime_type/1.0')
    media_type = bf_mime.media_type_for_mime_type(mime_type)
    if media_type == None:
      media_type = 'unknown'
    return media_type
