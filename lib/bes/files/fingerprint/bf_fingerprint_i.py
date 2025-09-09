#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import abc

class bf_fingerprint_i(abc.ABC):

  @abc.abstractmethod
  def checksum_sha(self, filename, algorithm, chunk_size, num_chunks):
    """Return the sha256 checksum for filename using algorithm."""
    raise NotImplementedError('checksum_sha')
  
  @abc.abstractmethod
  def checksum_sha256(self, filename, chunk_size, num_chunks):
    """Return the sha256 checksum for filename."""
    raise NotImplementedError('checksum_sha256')

  @abc.abstractmethod
  def checksum_sha512(self, filename):
    """Return the sha512 checksum for filename."""
    raise NotImplementedError('checksum_sha512')
