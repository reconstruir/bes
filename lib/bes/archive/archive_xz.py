#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, stat, tarfile

from bes.fs import file_util, temp_file
from bes.system import execute

from .archive import archive
from .archive_extension import archive_extension
from .archive_zip import archive_zip


class archive_xz(archive):
  'XZ archive.'

  _MAGIC = b'\xfd\x37\x7a\x58\x5a\x00'
  
  def __init__(self, filename):
    super(archive_xz, self).__init__(filename)

  @classmethod
  #@abstractmethod
  def file_is_valid(clazz, filename):
    with open(filename, 'rb') as fin:
      magic = fin.read(6)
      return magic == clazz._MAGIC

  #@abstractmethod
  def _get_members(self):
    with tarfile.open(self.filename, mode = 'r') as archive:
      return self._normalize_members([ member.path for member in archive.getmembers() ])
    
  @classmethod
  def _is_member(clazz, m):
    return m and not m.endswith('/')
  
  def has_member(self, arcname):
    return arcname in self.members
    
  def extract_members(self, members, dest_dir, base_dir = None,
                      strip_common_ancestor = False, strip_head = None,
                      include = None, exclude = None):
    # Cheat by using a temporary zip file to do the actual work.  Super innefecient but
    # easy since theres no library to extract just some stuff from dmg files.
    tmp_dir = temp_file.make_temp_dir()
    cmd = 'tar xf %s -C %s' % (self.filename, tmp_dir)
    execute.execute(cmd)
    tmp_zip = temp_file.make_temp_file(suffix = '.zip')
    az = archive_zip(tmp_zip)
    az.create(tmp_dir)
    az.extract_members(members, dest_dir, base_dir = base_dir,
                       strip_common_ancestor = strip_common_ancestor, strip_head = strip_head,
                       include = include, exclude = exclude)
    file_util.remove(tmp_zip)
    file_util.remove(tmp_dir)

  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    self._pre_create()
    items = self._find(root_dir, base_dir, extra_items, include, exclude)
    tmp_dir = temp_file.make_temp_dir()
    for item in items:
      file_util.copy(item.filename, path.join(tmp_dir, item.arcname))
    manifest_content = '\n'.join([ item.arcname for item in items ])
    manifest = temp_file.make_temp_file(content = manifest_content)
    cmd = 'tar Jcf %s -C %s -T %s' % (self.filename, tmp_dir, manifest)
    execute.execute(cmd)
    file_util.remove(tmp_dir)
