#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .archive import archive
from .archive_extension import archive_extension
from bes.fs import file_util

import os, os.path as path, zipfile

class archive_zip(archive):
  'A Zip archive class.'

  def __init__(self, filename):
    super(archive_zip, self).__init__(filename)

  def is_valid(self):
    return zipfile.is_zipfile(self.filename)

  def members(self):
    with zipfile.ZipFile(file = self.filename, mode = 'r') as archive:
      members = [ member.filename for member in archive.infolist() ]
      return self._normalize_members(members)

  def extract_members(self, members, dest_dir, base_dir = None,
                      strip_common_base = False, strip_head = None,
                      include = None, exclude = None):
    with zipfile.ZipFile(file = self.filename, mode = 'r') as archive:
      dest_dir = self._determine_dest_dir(dest_dir, base_dir)
      for member in self._filter_for_extract(members, include, exclude):
        archive.extract(member, path = dest_dir)
      self._handle_extract_strip_common_base(members, strip_common_base, strip_head, dest_dir)

  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    assert file_util.extension(self.filename).lower() == archive_extension.ZIP
    self._pre_create()
    items = self._find(root_dir, base_dir, extra_items, include, exclude)
    with zipfile.ZipFile(file = self.filename, mode = 'w', compression = zipfile.ZIP_DEFLATED) as archive:
      for item in items:
        archive.write(item.filename, arcname = item.arcname)
