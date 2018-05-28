#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, tarfile
from bes.system import execute

from .archive import archive
from .archive_extension import archive_extension

class archive_unix_tar(archive):
  'Deal with archives using the unix tar binary.'

  def __init__(self, filename):
    super(archive_unix_tar, self).__init__(filename)
    self._members = None

  def is_valid(self):
    try:
      self.members()
      return True
    except Exception as ex:
      pass
    return False

  def _cached_members(self):
    cmd = 'tar tf %s' % (self.filename)
    rv = execute.execute(cmd)
    return [ m for m in rv.stdout.split('\n') if self._is_member(m) ]
  
  def members(self):
    cmd = 'tar tf %s' % (self.filename)
    rv = execute.execute(cmd)
    return [ m for m in rv.stdout.split('\n') if self._is_member(m) ]

  @classmethod
  def _is_member(clazz, m):
    return m and not m.endswith('/')
  
  def has_member(self, arcname):
    with tarfile.open(self.filename, mode = 'r') as archive:
      try:
        archive.getmember(arcname)
        return True
      except KeyError as ex:
        return False
    
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
