#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import abc

from bes.system.check import check

class bf_fingerprint_i(abc.ABC):

  @abc.abstractmethod
  def checksum_sha(self, filename, algorithm, chunk_size, num_chunks):
    """Return checksum for filename using sha algorithm."""
    raise NotImplementedError('checksum_sha')

  SHORT_CHECKSUM_SIZE = 1024 * 1024
  
  @abc.abstractmethod
  def checksum_short_sha(self, filename, algorithm):
    """Return a short checksum for filename using sha algorithm."""
    raise NotImplementedError('checksum_short_sha')

check.register_class(bf_fingerprint_i, name = 'bf_fingerprint', include_seq = False)
