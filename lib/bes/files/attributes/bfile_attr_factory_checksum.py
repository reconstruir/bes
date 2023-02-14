#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..bfile_checksum import bfile_checksum

from .bfile_attr_factory_base import bfile_attr_factory_base

class bfile_attr_factory_checksum(bfile_attr_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      ( 'bes', 'checksum_md5', '1.0', lambda f: bfile_checksum(f, 'md5', clazz.decode_string, False ),
      ( 'bes', 'checksum_sha1', '1.0', lambda f: bfile_checksum(f, 'sha1', clazz.decode_string, False ),
      ( 'bes', 'checksum_sha256', '1.0', lambda f: bfile_checksum(f, 'sha256', clazz.decode_string, False ),
    ]
