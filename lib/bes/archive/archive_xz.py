#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .archive import archive
from .archive_extension import archive_extension
from bes.fs import file_util

import os, os.path as path, stat

class archive_xz(archive):
  'XZ archive.'

  _MAGIC = b'\xfd\x37\x7a\x58\x5a\x00'
  
  def __init__(self, filename):
    super(archive_xz, self).__init__(filename)

  def is_valid(self):
    with open(self.filename, 'rb') as fin:
      magic = fin.read(6)
      return magic == self._MAGIC

  def members(self):
    assert False

  def has_member(self, arcname):
    assert False
    
  def extract_members(self, members, dest_dir, base_dir = None,
                      strip_common_base = False, strip_head = None,
                      include = None, exclude = None):
    assert False

  def create(self, root_dir, base_dir = None,
             extra_items = None,
             include = None, exclude = None):
    assert False
