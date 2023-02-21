#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_checksum import bfile_checksum

from ..metadata.bfile_metadata_factory_base import bfile_metadata_factory_base

class bfile_metadata_factory_checksum(bfile_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      ( 'bes/checksum/md5/0.0', lambda f: bfile_checksum.checksum(f, 'md5'), clazz.decode_string, clazz.encode_string, check.check_string, ( 'bes_checksum_md5', ) ),
      ( 'bes/checksum/sha1/0.0', lambda f: bfile_checksum.checksum(f, 'sha1'), clazz.decode_string, clazz.encode_string, check.check_string, ( 'bes_checksum_sha1', ) ),
      ( 'bes/checksum/sha256/0.0', lambda f: bfile_checksum.checksum(f, 'sha256'), clazz.decode_string, clazz.encode_string, check.check_string, ( 'bes_checksum_sha256', ) ),
    ]
