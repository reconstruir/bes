#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib

from bes.system.check import check
from bes.system.log import logger

from ..bf_check import bf_check

from .bf_hasher_base import bf_hasher_base

class bf_hasher_hashlib(bf_hasher_base):

  _log = logger('bf_hasher')

  #@abc.abstractmethod
  def checksum_sha(self, filename, algorithm, chunk_size, num_chunks):
    """Return checksum for filename using sha algorithm."""
    filename = bf_check.check_file(filename)
    check.check_string(algorithm)
    check.check_int(chunk_size, allow_none = True)
    check.check_int(num_chunks, allow_none = True)
    
    self._log.log_method_d()
    
    chunk_size = chunk_size or (1024 * 1024)
    hasher = hashlib.new(algorithm)
    with open(filename, 'rb') as fin: 
      for chunk_index, chunk in enumerate(iter(lambda: fin.read(chunk_size), b''), start = 1):
        hasher.update(chunk)
        if num_chunks == chunk_index:
          break
    return hasher.hexdigest()

  #@abc.abstractmethod
  def short_checksum_sha(self, filename, algorithm):
    """Return a short checksum for filename using sha algorithm."""
    return self.checksum_sha(filename, algorithm, self.SHORT_CHECKSUM_SIZE, 1)
