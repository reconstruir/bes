#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .bf_hasher_i import bf_hasher_i

class bf_hasher_base(bf_hasher_i):
  
  def checksum_sha256(self, filename, chunk_size = None, num_chunks = None):
    """Return the sha256 checksum for filename."""
    return self.checksum_sha(filename, 'sha256', chunk_size, num_chunks)

  def checksum_sha512(self, filename, chunk_size = None, num_chunks = None):
    """Return the sha512 checksum for filename."""
    return self.checksum_sha(filename, 'sha512', chunk_size, num_chunks)

  #@abc.abstractmethod
  def checksum_md5(self, filename, chunk_size = None, num_chunks = None):
    """Return checksum for filename using md5 algorithm."""
    return self.checksum_sha(filename, 'md5', chunk_size, num_chunks)
