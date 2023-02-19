#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_checksum import bfile_checksum

from ..metadata.bfile_metadata_factory_base import bfile_metadata_factory_base

class bfile_metadata_factory_checksum(bfile_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    def fuck(f):
      if clazz.metadata_class.has_key(f, 'bes/checksum/sha256/0.0'):
        return clazz.metadata_class.get_string(f, 'bes/checksum/sha256/0.0')
      elif clazz.metadata_class.has_key(f, 'bes_checksum_sha256'):
        return clazz.metadata_class.get_string(f, 'bes_checksum_sha256')
      return bfile_checksum.checksum(f, 'sha256')
    
    return [
      ( 'bes/checksum/md5/0.0', lambda f: bfile_checksum.checksum(f, 'md5'), clazz.decode_string, clazz.encode_string, True ),
      ( 'bes/checksum/sha1/0.0', lambda f: bfile_checksum.checksum(f, 'sha1'), clazz.decode_string, clazz.encode_string, True ),
      #( 'bes/checksum/sha256/0.0', lambda f: bfile_checksum.checksum(f, 'sha256'), clazz.decode_string, clazz.encode_string, True ),
      ( 'bes/checksum/sha256/0.0', fuck, clazz.decode_string, clazz.encode_string, True ),
    ]
