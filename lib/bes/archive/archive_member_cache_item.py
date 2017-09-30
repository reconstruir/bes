#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from .archiver import archiver
from bes.fs import file_checksum, file_cacheItemInterface, file_util

class archive_member_cache_item(file_cacheItemInterface):
  def __init__(self, archive, member):
    super(archive_member_cache_item, self).__init__()
    self._archive = path.abspath(path.normpath(archive))
    self._member = member
    self._checksum = file_checksum.checksum(self._archive).checksum
    
  def save(self, info):
    assert archiver.is_valid(self._archive)
    archiver.extract_member_to_file(self._archive, self._member, info.cached_filename)
    # The checksum here is for the archive not the member
    file_util.save(info.checksum_filename, self._checksum + '\n')

  def checksum(self):
    return self._checksum

  def name(self):
    return path.join(self._archive, self._member)

  def load(self, cached_filename):
    return file_util.read(cached_filename)
