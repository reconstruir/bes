#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import string_util
from bes.fs import file_util, temp_file

from .git import git
from .git_util import git_util

class git_download_cache(object):
  'A git download cache.'

  def __init__(self, root_dir):
    self.root_dir = root_dir
    
  def has_tarball(self, address, revision):
    'Return True if the tarball with address and revision is in the cache.'
    local_address_path = self._address_path(address)
    tarball_filename = '%s.tar.gz' % (revision)
    tarball_path = path.join(local_address_path, tarball_filename)
    return path.exists(tarball_path)

  def get_tarball(self, address, revision):
    'Return the local filesystem path to the tarball with address and revision.'
    local_address_path = self._address_path(address)
    tarball_filename = '%s.tar.gz' % (revision)
    tarball_path = path.join(local_address_path, tarball_filename)
    if path.exists(tarball_path):
      return tarball_path
    tmp_dir = temp_file.make_temp_dir()
    name = git_util.name_from_address(address)
    tmp_full_path = path.join(tmp_dir, tarball_filename)
    git.download_tarball(name, revision, address, tmp_full_path)
    file_util.rename(tmp_full_path, tarball_path)
    return tarball_path
    
  def _address_path(self, address):
    'Return path for local tarball.'
    return path.join(self.root_dir, self._sanitize_address(address))

  @classmethod
  def _sanitize_address(clazz, address):
    'Return path for local tarball.'
    return string_util.replace(address, { ':': '_', '/': '_' })
