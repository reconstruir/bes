#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from archive import archive
from archive_extension import archive_extension

import os.path as path, tarfile

class archive_tar(archive):
  'A Tar archive class.'

  def __init__(self, filename):
    super(archive_tar, self).__init__(filename)

  def is_valid(self):
    return tarfile.is_tarfile(self.filename)

  def members(self):
    with tarfile.open(self.filename, mode = 'r') as archive:
      members = [ member.path for member in archive.getmembers() ]
      return self._normalize_members(members)

  def extract_members(self, members, dest_dir, base_dir = None,
                      strip_common_base = False, strip_head = None,
                      include = None, exclude = None):
    with tarfile.open(self.filename, mode = 'r') as archive:
      dest_dir = self._determine_dest_dir(dest_dir, base_dir)
      filtered_members = self._filter_for_extract(members, include, exclude)
      if filtered_members == self.members():
        archive.extractall(path = dest_dir)
      else:
        for member in filtered_members:
          archive.extract(member, path = dest_dir)
      self._handle_extract_strip_common_base(members, strip_common_base, strip_head, dest_dir)

  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    self._pre_create()
    items = self._find(root_dir, base_dir, extra_items, include, exclude)
    mode = archive_extension.write_format_for_filename(self.filename)
    with tarfile.open(self.filename, mode = mode) as archive:
      for item in items:
        archive.add(item.filename, arcname = item.arcname)
