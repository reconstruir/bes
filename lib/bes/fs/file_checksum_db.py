#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from .file_util import file_util
from .file_checksum_attributes import file_checksum_attributes

from .file_metadata import file_metadata

class file_checksum_db(object):

  _KEY_BES_MTIME = 'bes.mtime'
  _KEY_BES_CHECKSUM_MD5 = 'bes.checksum.md5'
  _KEY_BES_CHECKSUM_SHA1 = 'bes.checksum.sha1'
  _KEY_BES_CHECKSUM_SHA256 = 'bes.checksum.sha256'

  _ALGORITHM_TO_KEY = {
    'md5': _KEY_BES_CHECKSUM_MD5,
    'sha1': _KEY_BES_CHECKSUM_SHA1,
    'sha256': _KEY_BES_CHECKSUM_SHA256,
  }
  
  def __init__(self, db_filename):
    check.check_string(db_filename)
    self._db_filename = db_filename
    self._metadata = file_metadata(self._db_filename)
    self._count = 0

  @property
  def count(self):
    return self._count
  
  def checksum(self, algorithm, filename, chunk_size = None):
    check.check_string(filename)
    checksum_key = self._ALGORITHM_TO_KEY.get(algorithm, None)
    if not checksum_key:
      raise ValueError('invalid algorithm: %s' % (algorithm))
    attr_mtime = self._metadata.get_value(filename, self._KEY_BES_MTIME)
    attr_checksum = self._metadata.get_value(filename, checksum_key)
    if attr_mtime is not None and attr_checksum is not None:
      if attr_mtime == str(file_util.mtime(filename)):
        return attr_checksum
    return self._write_checksum(algorithm, filename, chunk_size)

  def _write_checksum(self, algorithm, filename, chunk_size):
    mtime = str(file_util.mtime(filename))
    checksum = file_util.checksum(algorithm, filename)
    self._count += 1
    checksum_key = self._ALGORITHM_TO_KEY.get(algorithm, None)
    try:
      self._metadata.set_value(filename, self._KEY_BES_MTIME, mtime)
      self._metadata.set_value(filename, checksum_key, checksum)
    except Exception as ex:
      print('ERROR: Failed to write checksum for %s to db %s' % (filename, self._db_filename))
      pass
    return checksum
  
