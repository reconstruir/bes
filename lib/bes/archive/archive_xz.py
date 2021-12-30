#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path
import stat
import tarfile

from bes.system.log import logger

from .archive import archive
from .archive_extension import archive_extension

class archive_xz(archive):
  'XZ archive.'

  _log = logger('archive_xz')
  
  # https://tukaani.org/xz/xz-file-format.txt
  _MAGIC = b'\xfd\x37\x7a\x58\x5a\x00'
  
  def __init__(self, filename):
    super(archive_xz, self).__init__(filename)

  @classmethod
  #@abstractmethod
  def name(clazz, filename):
    'Name of this archive format.'
    return 'xz'
    
  @classmethod
  #@abstractmethod
  def file_is_valid(clazz, filename):
    with open(filename, 'rb') as fin:
      magic = fin.read(len(clazz._MAGIC))
      return magic == clazz._MAGIC

  #@abstractmethod
  def _get_members(self):
    with tarfile.open(self.filename, mode = 'r') as archive:
      return self._normalize_members([ self._member_path(member) for member in archive.getmembers() ])

  #@abstractmethod
  def _member_path(clazz, member):
    if member.isdir():
      return '{}/'.format(member.path)
    return member.path
  
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

  #@abstractmethod
  def extract(self, dest_dir, base_dir = None,
              strip_common_ancestor = False, strip_head = None,
              include = None, exclude = None):
    filtered_members = self._filter_for_extract(self.members, include, exclude)
    if filtered_members == self.members:
      return self.extract_all(dest_dir,
                              base_dir = base_dir,
                              strip_common_ancestor = strip_common_ancestor,
                              strip_head = strip_head)
    dest_dir = self._determine_dest_dir(dest_dir, base_dir)
    with tarfile.open(self.filename, mode = 'r') as archive:
      for member in filtered_members:
        archive.extract(member, path = dest_dir)
      self._handle_extract_strip_common_ancestor(filtered_members, strip_common_ancestor, strip_head, dest_dir)

  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None,
             extension = None):
    self._pre_create()
    items = self._find(root_dir, base_dir, extra_items, include, exclude)
    self._log.log_d('create: extension={} filename={}'.format(extension, self.filename))
    if extension:
      mode = archive_extension.write_format(extension)
    else:
      mode = archive_extension.write_format_for_filename(self.filename)
    self._log.log_d('create: mode={}'.format(mode))
    with tarfile.open(self.filename, mode = mode) as archive:
      for item in items:
        archive.add(item.filename, arcname = item.arcname)
