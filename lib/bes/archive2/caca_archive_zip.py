#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .archive import archive
from .archive_extension import archive_extension
from bes.fs import file_util

import os, os.path as path, stat, zipfile

class archive_zip(archive):
  'A Zip archive class.'

  def __init__(self, filename):
    super(archive_zip, self).__init__(filename)

  @classmethod
  #@abstractmethod
  def file_is_valid(clazz, filename):
    return zipfile.is_zipfile(filename)

  #@abstractmethod
  def _get_members(self):
    with zipfile.ZipFile(file = self.filename, mode = 'r') as archive:
      return self._normalize_contents([ m.filename for m in archive.infolist() ])
  
  #@abstractmethod
  def has_member(self, filename):
    '''Return True if filename is part of contents.  Note that directories should end in "/" '''
    with zipfile.ZipFile(file = self.filename, mode = 'r') as archive:
      try:
        archive.getinfo(filename)
        return True
      except KeyError as ex:
        pass
      return False

  #@abstractmethod
  def extract_all(self, dest_dir, base_dir = None,
                  strip_common_ancestor = False, strip_head = None):
    with zipfile.ZipFile(file = self.filename, mode = 'r') as archive:
      dest_dir = self._determine_dest_dir(dest_dir, base_dir)
      archive.extractall(path = dest_dir)
    self._handle_extract_strip_common_ancestor(self.contents, strip_common_ancestor, strip_head, dest_dir)

  #@abstractmethod
  def extract(self, dest_dir, base_dir = None,
              strip_common_ancestor = False, strip_head = None,
              include = None, exclude = None):
    dest_dir = self._determine_dest_dir(dest_dir, base_dir)
    filtered_contents = self._filter_for_extract(self.contents, include, exclude)
    if filtered_contents == self.contents:
      self.extract_all(dest_dir, base_dir = base_dir, strip_common_ancestor = strip_common_ancestor,
                       strip_head = strip_head)
      return
    with zipfile.ZipFile(file = self.filename, mode = 'r') as archive:
      zip_infos = self._infos_for_files(archive, filtered_filenames)
      for zip_info in zip_infos:
        extracted = archive.extract(zip_info, path = dest_dir)
        self._fix_permissions(extracted, zip_info)
      self._handle_extract_strip_common_ancestor(filtered_contents, strip_common_ancestor, strip_head, dest_dir)

  #@abstractmethod
  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    assert file_util.extension(self.filename).lower() == archive_extension.ZIP
    self._pre_create()
    items = self._find(root_dir, base_dir, extra_items, include, exclude)
    with zipfile.ZipFile(file = self.filename, mode = 'w', compression = zipfile.ZIP_DEFLATED) as archive:
      for item in items:
        archive.write(item.filename, arcname = item.arcname)

  @classmethod
  def _infos_for_files(clazz, archive, filenames):
    return [ archive.getinfo(filename) for filename in filenames ]

  _ZIP_UNIX_SYSTEM = 3
  @classmethod
  def _fix_permissions(clazz, filename, info):
    'From https://stackoverflow.com/questions/42326428/zipfile-in-python-file-permission'
    if not path.isfile(filename):
      return
    if info.create_system != clazz._ZIP_UNIX_SYSTEM:
      return
    unix_attributes = info.external_attr >> 16
    if unix_attributes & stat.S_IXUSR:
      os.chmod(filename, os.stat(filename).st_mode | stat.S_IXUSR)
