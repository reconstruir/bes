#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib
import os
from os import path

class bf_checksum_fingerprint:

  VERSION = 1
  HEAD_TAIL_PROBE_BYTES = 4096

  @classmethod
  def make_key(clazz, filename):
    'Return the sha256 fingerprint key for filename.'
    stat_result = os.stat(filename)
    size = stat_result.st_size
    mtime_ns = stat_result.st_mtime_ns
    basename = path.basename(filename)

    head_hash, tail_hash = clazz._compute_head_tail(filename, size)

    version_hex = f'{clazz.VERSION & 0xFFFF_FFFF_FFFF_FFFF:016x}'
    size_hex    = f'{size & 0xFFFF_FFFF_FFFF_FFFF:016x}'
    mtime_hex   = f'{mtime_ns & 0xFFFF_FFFF_FFFF_FFFF:016x}'

    serialized = '\x00'.join([version_hex, basename, size_hex, mtime_hex, head_hash, tail_hash])
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

  @classmethod
  def _compute_head_tail(clazz, filename, size):
    if size == 0:
      empty_hash = hashlib.md5(b'').hexdigest()
      return empty_hash, empty_hash

    probe = clazz.HEAD_TAIL_PROBE_BYTES
    with open(filename, 'rb') as f:
      head_data = f.read(probe)
      head_hash = hashlib.md5(head_data).hexdigest()

      if size <= probe:
        return head_hash, head_hash

      f.seek(size - probe)
      tail_data = f.read(probe)
      tail_hash = hashlib.md5(tail_data).hexdigest()

    return head_hash, tail_hash
