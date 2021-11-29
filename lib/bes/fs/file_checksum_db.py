#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.system.log import logger

from .file_util import file_util
from .file_checksum_attributes import file_checksum_attributes

from .file_metadata import file_metadata

class file_checksum_db(object):

  log = logger('file_checksum_db')
  
  _KEY_BES_MTIME = 'bes.mtime'
  _KEY_BES_CHECKSUM_MD5 = 'bes.checksum.md5'
  _KEY_BES_CHECKSUM_SHA1 = 'bes.checksum.sha1'
  _KEY_BES_CHECKSUM_SHA256 = 'bes.checksum.sha256'

  _ALGORITHM_TO_KEY = {
    'md5': _KEY_BES_CHECKSUM_MD5,
    'sha1': _KEY_BES_CHECKSUM_SHA1,
    'sha256': _KEY_BES_CHECKSUM_SHA256,
  }

  DEFAULT_CHECKSUM_DB_FILENAME = '.bes_file_checksum.db'
  
  def __init__(self, root_dir, db_filename = None):
    check.check_string(root_dir)
    check.check_string(db_filename, allow_none = True)
    db_filename = db_filename or self.DEFAULT_CHECKSUM_DB_FILENAME
    
    self._metadata = file_metadata(root_dir, db_filename = db_filename)
    self._count = 0

  @property
  def count(self):
    return self._count
  
  def checksum(self, algorithm, filename, chunk_size = None):
    check.check_string(algorithm)
    check.check_string(filename)
    check.check_int(chunk_size, allow_none = True)
    self.log.log_d('checksum: algorithm={} filename={}'.format(algorithm, filename))
    checksum_key = self._ALGORITHM_TO_KEY.get(algorithm, None)
    if not checksum_key:
      raise ValueError('invalid algorithm: %s' % (algorithm))
    attr_mtime = self._metadata.get_value('checksums', filename, self._KEY_BES_MTIME)
    attr_checksum = self._metadata.get_value('checksums', filename, checksum_key)
    mtime = file_util.mtime(filename)
    self.log.log_d('checksum: mtime={} attr_mtime={} attr_checksum={}'.format(mtime, attr_mtime, attr_checksum))
    if attr_mtime is not None and attr_checksum is not None:
      if attr_mtime == str(file_util.mtime(filename)):
        return attr_checksum
    return self._write_checksum(algorithm, filename, chunk_size)

  def _write_checksum(self, algorithm, filename, chunk_size):
    mtime = str(file_util.mtime(filename))
    checksum = file_util.checksum(algorithm, filename)
    self._count += 1
    checksum_key = self._ALGORITHM_TO_KEY.get(algorithm, None)
    self.log.log_d('_write_checksum: mtime={} checksum={} count={} checksum_key={}'.format(mtime,
                                                                                           checksum,
                                                                                           self._count,
                                                                                           checksum_key))
    try:
# it seems it would be better to update both of these at once but for some reason
# this doesnt work.      
#      values = {
#        self._KEY_BES_MTIME: mtime,
#        checksum_key: checksum,
#      }
#      self._metadata.replace_values(filename, values)
      self._metadata.set_value('checksums', filename, self._KEY_BES_MTIME, mtime)
      self._metadata.set_value('checksums', filename, checksum_key, checksum)
    except Exception as ex:
      self.log.log_e('_write_checksum: Failed to write checksum for {} to {}'.format(filename,
                                                                                     self._metadata.db_filename))
    return checksum
  
