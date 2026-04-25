#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path
from .archiver import archiver
from bes.fs.file_cache_item_base import file_cache_item_base
from bes.files.bf_file_ops import bf_file_ops

class archive_member_cache_item(file_cache_item_base):
  def __init__(self, archive, member):
    super(archive_member_cache_item, self).__init__()
    self._archive = path.abspath(path.normpath(archive))
    self._member = member
    self._checksum = bf_file_ops.checksum('sha256', self._archive)
    
  def save(self, info):
    assert archiver.is_valid(self._archive)
    archiver.extract_member_to_file(self._archive, self._member, info.cached_filename)
    # The checksum here is for the archive not the member
    bf_file_ops.save(info.checksum_filename, self._checksum + '\n')

  def checksum(self):
    return self._checksum

  def name(self):
    return path.join(self._archive, self._member)

  def load(self, cached_filename):
    return bf_file_ops.read(cached_filename)
