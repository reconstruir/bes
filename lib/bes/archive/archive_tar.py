#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, tarfile

from bes.fs import tar_util

from .archive import archive
from .archive_extension import archive_extension

class archive_tar(archive):
  'A Tar archive class.'

  def __init__(self, filename):
    super(archive_tar, self).__init__(filename)

  @classmethod
  #@abstractmethod
  def file_is_valid(clazz, filename):
    return tarfile.is_tarfile(filename)

  #@abstractmethod
  def _get_members(self):
    with tarfile.open(self.filename, mode = 'r') as archive:
      return self._normalize_members([ member.path for member in archive.getmembers() ])

  #@abstractmethod
  def has_member(self, member):
    '''Return True if filename is part of members.  Note that directories should end in "/" '''
    with tarfile.open(self.filename, mode = 'r') as archive:
      try:
        archive.getmember(member)
        return True
      except KeyError as ex:
        pass
    return False

  #@abstractmethod
  def extract_all(self, dest_dir, base_dir = None,
                  strip_common_ancestor = False, strip_head = None):
    with tarfile.open(self.filename, mode = 'r') as archive:
      dest_dir = self._determine_dest_dir(dest_dir, base_dir)
      archive.extractall(path = dest_dir)
      self._handle_extract_strip_common_ancestor(self.members, strip_common_ancestor, strip_head, dest_dir)
  
  def extract_members(self, members, dest_dir, base_dir = None,
                      strip_common_ancestor = False, strip_head = None,
                      include = None, exclude = None):
    with tarfile.open(self.filename, mode = 'r') as archive:
      dest_dir = self._determine_dest_dir(dest_dir, base_dir)
      filtered_members = self._filter_for_extract(members, include, exclude)
      if filtered_members == self.members:
        archive.extractall(path = dest_dir)
      else:
        for member in filtered_members:
          archive.extract(member, path = dest_dir)
      self._handle_extract_strip_common_ancestor(members, strip_common_ancestor, strip_head, dest_dir)

  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    self._pre_create()
    items = self._find(root_dir, base_dir, extra_items, include, exclude)
    mode = archive_extension.write_format_for_filename(self.filename)
    with tarfile.open(self.filename, mode = mode) as archive:
      for item in items:
        archive.add(item.filename, arcname = item.arcname)
