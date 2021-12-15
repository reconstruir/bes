#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from .file_util import file_util
from .file_attributes_metadata import file_attributes_metadata

class file_checksum_attributes(object):

  _KEY_BES_CHECKSUM_MD5 = 'bes_checksum_md5'
  _KEY_BES_CHECKSUM_SHA1 = 'bes_checksum_sha1'
  _KEY_BES_CHECKSUM_SHA256 = 'bes_checksum_sha256'

  _ALGORITHM_TO_KEY = {
    'md5': _KEY_BES_CHECKSUM_MD5,
    'sha1': _KEY_BES_CHECKSUM_SHA1,
    'sha256': _KEY_BES_CHECKSUM_SHA256,
  }
  
  @classmethod
  def checksum(clazz, algorithm, filename, chunk_size = None):
    check.check_string(algorithm)
    check.check_string(filename)
    check.check_int(chunk_size, allow_none = True)

    checksum_key = clazz._ALGORITHM_TO_KEY.get(algorithm, None)
    if not checksum_key:
      raise ValueError('invalid algorithm: {}'.format(algorithm))

    def _checksum_maker():
      chk = file_util.checksum(algorithm, filename, chunk_size = chunk_size)
      return chk.encode('utf-8')
    return file_attributes_metadata.get_bytes(filename, checksum_key, _checksum_maker).decode('utf-8')
