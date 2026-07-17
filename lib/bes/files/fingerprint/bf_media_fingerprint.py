#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# Cheap sampled content fingerprint for large media files.  This is
# cache-key-quality identity, NOT an integrity checksum: only the size plus
# the head, the tail and a few interior samples are hashed, so two files that
# differ only in an unsampled region collide by construction.  Use it to key
# derived artifacts (thumbnails, transcodes, analysis results) where a
# collision costs a stale artifact; never use it for dedup, sync or corruption
# detection - that is what bf_checksum_cache is for.  Small files are hashed
# in full; large files cost a fixed few-hundred-KB read regardless of size.
#
# The sampling constants define the fingerprint value, and callers persist
# fingerprints on disk (e.g. the bav preview cache uses them as directory
# names).  Changing any constant silently orphans every artifact keyed by the
# old values; treat them as frozen and have callers version their persisted
# keys if the algorithm must ever change.

import hashlib
import os
import threading

from os import path

from ..bf_check import bf_check

class bf_media_fingerprint(object):

  SIZE_THRESHOLD = 1_048_576
  HEAD_BYTES = 65536
  TAIL_BYTES = 65536
  MID_SAMPLES = 3
  SAMPLE_BYTES = 4096

  _cache = {}
  _cache_lock = threading.Lock()
  _CACHE_MAX_ENTRIES = 8192

  @classmethod
  def fingerprint(clazz, filename):
    'Return the sampled content fingerprint for filename, cached per (path, size, mtime).'
    filename = bf_check.check_file(filename)

    filename = path.abspath(filename)
    stat_result = os.stat(filename)
    cache_key = ( filename, stat_result.st_size, stat_result.st_mtime_ns )
    with clazz._cache_lock:
      cached = clazz._cache.get(cache_key, None)
    if cached is not None:
      return cached
    result = clazz._compute(filename, stat_result.st_size)
    with clazz._cache_lock:
      if len(clazz._cache) >= clazz._CACHE_MAX_ENTRIES:
        clazz._cache.clear()
      clazz._cache[cache_key] = result
    return result

  @classmethod
  def clear_cache(clazz):
    'Drop every cached fingerprint.  Mainly for tests.'
    with clazz._cache_lock:
      clazz._cache.clear()

  @classmethod
  def _compute(clazz, filename, size):
    hasher = hashlib.sha256()
    hasher.update(size.to_bytes(8, 'big'))
    with open(filename, 'rb') as fin:
      if size <= clazz.SIZE_THRESHOLD:
        hasher.update(fin.read())
        return hasher.hexdigest()
      hasher.update(fin.read(clazz.HEAD_BYTES))
      for i in range(1, clazz.MID_SAMPLES + 1):
        offset = size * i // (clazz.MID_SAMPLES + 1)
        fin.seek(offset)
        hasher.update(fin.read(clazz.SAMPLE_BYTES))
      fin.seek(max(size - clazz.TAIL_BYTES, clazz.HEAD_BYTES))
      hasher.update(fin.read(clazz.TAIL_BYTES))
    return hasher.hexdigest()
