#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..checksum.bf_checksum import bf_checksum

from ..metadata.bf_metadata_factory_base import bf_metadata_factory_base

from ..attr.bf_attr_type_desc_string import bf_attr_type_desc_string

class bf_metadata_factory_checksum(bf_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def descriptions(clazz):
    return [
      (
        'bes/checksum/md5/0.0',
        'MD5 Checksum',
        lambda f: bf_checksum.checksum(f, 'md5'),
        bf_attr_type_desc_string,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_checksum_md5')
      ),
      (
        'bes/checksum/sha1/0.0',
        'SHA1 Checksum',
        lambda f: bf_checksum.checksum(f, 'sha1'),
        bf_attr_type_desc_string,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_checksum_sha1')
      ),
      (
        'bes/checksum/sha256/0.0',
        'SHA256 Checksum',
        lambda f: bf_checksum.checksum(f, 'sha256'),
        bf_attr_type_desc_string,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_checksum_sha256')
      ),
    ]
