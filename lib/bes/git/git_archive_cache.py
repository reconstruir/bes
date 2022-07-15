#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from ..system.check import check
from bes.common.string_util import string_util
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from .git import git
from .git_address_util import git_address_util

class git_archive_cache(object):
  'A git download by revision cache.'

  def __init__(self, root_dir):
    self.root_dir = root_dir
    
  def has_tarball(self, address, revision):
    'Return True if the tarball with address and revision is in the cache.'
    local_address_path = self.path_for_address(address)
    tarball_filename = '%s.tar.gz' % (revision)
    tarball_path = path.join(local_address_path, tarball_filename)
    return path.exists(tarball_path)

  def get_tarball(self, address, revision):
    'Return the local filesystem path to the tarball with address and revision.'
    local_address_path = self.path_for_address(address)
    tarball_filename = '%s.tar.gz' % (revision)
    tarball_path = path.join(local_address_path, tarball_filename)
    if path.exists(tarball_path):
      return tarball_path
    tmp_dir = temp_file.make_temp_dir()
    if path.isdir(address):
      name = path.basename(address)
    else:
      name = git_address_util.name(address)
    tmp_full_path = path.join(tmp_dir, tarball_filename)
    git.archive(address, revision, name, tmp_full_path)
    file_util.rename(tmp_full_path, tarball_path)
    return tarball_path
    
  def path_for_address(self, address):
    'Return path for local tarball.'
    return path.join(self.root_dir, git_address_util.sanitize_for_local_path(address))

  def tarball_path(self, address, revision):
    'Return True if the tarball with address and revision is in the cache.'
    local_address_path = self.path_for_address(address)
    tarball_filename = '%s.tar.gz' % (revision)
    return path.join(local_address_path, tarball_filename)
  
check.register_class(git_archive_cache, include_seq = False)
