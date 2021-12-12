#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .file_util import file_util
from .file_attributes import file_attributes

class file_checksum_attributes(object):

  _KEY_BES_MTIME = 'bes.mtime'
  _KEY_BES_CHECKSUM_MD5 = 'bes.checksum.md5'
  _KEY_BES_CHECKSUM_SHA1 = 'bes.checksum.sha1'
  _KEY_BES_CHECKSUM_SHA256 = 'bes.checksum.sha256'

  _ALGORITHM_TO_KEY = {
    'md5': _KEY_BES_CHECKSUM_MD5,
    'sha1': _KEY_BES_CHECKSUM_SHA1,
    'sha256': _KEY_BES_CHECKSUM_SHA256,
  }
  
  @classmethod
  def checksum(clazz, algorithm, filename, chunk_size = None):
    checksum_key = clazz._ALGORITHM_TO_KEY.get(algorithm, None)
    if not checksum_key:
      raise ValueError('invalid algorithm: %s' % (algorithm))
    attr_mtime = file_attributes.get_bytes(filename, clazz._KEY_BES_MTIME)
    attr_checksum = file_attributes.get_bytes(filename, checksum_key)
    if attr_mtime is not None and attr_checksum is not None:
      if attr_mtime == str(file_util.mtime(filename)):
        #print('GOOD: %s' % (filename))
        return attr_checksum
    #print('BAD: %s' % (filename))
    return clazz._write_checksum(algorithm, filename, chunk_size)

  @classmethod
  def _write_checksum(clazz, algorithm, filename, chunk_size):
    mtime = str(file_util.mtime(filename))
    checksum = file_util.checksum(algorithm, filename)
    checksum_key = clazz._ALGORITHM_TO_KEY.get(algorithm, None)
    try:
      file_attributes.set_bytes(filename, clazz._KEY_BES_MTIME, mtime.encode('utf-8'))
      file_attributes.set_bytes(filename, checksum_key, checksum.encode('utf-8'))
    finally:
      pass
#      try:
#        file_attributes.remove(filename, clazz._KEY_BES_MTIME)
#        file_attributes.remove(filename, checksum_key)
#      except Exception as ex:
#        pass
    return checksum
