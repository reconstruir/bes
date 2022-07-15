#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from ..system.check import check
from bes.common.string_util import string_util
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from .git import git
from .git_address_util import git_address_util
from .git_repo import git_repo
from .git_clone_options import git_clone_options

class git_clone_manager(object):
  'Manage a collection of repos under one root dir with conveniences.'

  def __init__(self, root_dir):
    self.root_dir = path.expanduser(root_dir)
    
  def update(self, address, options = None):
    'Update the repo.'
    repo_path = self.path_for_address(address)
    repo = git_repo(repo_path, address = address)
    repo.clone_or_pull(options = options)
    return repo
    
  def path_for_address(self, address):
    'Return path for local tarball.'
    return path.join(self.root_dir, git_address_util.sanitize_for_local_path(address))

check.register_class(git_clone_manager, include_seq = False)
