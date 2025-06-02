#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..checksum.bf_checksum import bf_checksum
from ..mime.bf_mime import bf_mime

from ..metadata.bf_metadata_factory_base import bf_metadata_factory_base

from ..attr.bf_attr_type_desc_string import bf_attr_type_desc_string

class bf_metadata_factory_mime(bf_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def descriptions(clazz):
    return [
      (
        'bes__mime__mime_type__1.0',
        'Mime Type',
        lambda f: bf_mime.mime_type(f),
        bf_attr_type_desc_string,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_mime_type')
      ),
      (
        'bes__mime__media_type__1.0',
        'Media Type',
        lambda f: clazz._media_type_1_0(f),
        bf_attr_type_desc_string,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_media_type')
      )
    ]
  
  @classmethod
  def _media_type_1_0(clazz, filename):
    mime_type = clazz.metadata.get_metadata(filename, 'bes__mime__mime_type__1.0')
    media_type = bf_mime.media_type_for_mime_type(mime_type)
    if media_type == None:
      media_type = 'unknown'
    return media_type
