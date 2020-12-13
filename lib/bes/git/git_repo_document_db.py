# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect
from os import path

from bes.git.git_address_util import git_address_util
from bes.git.git_repo import git_repo
from bes.fs.file_util import file_util
from bes.common.check import check
from bes.git.git_error import git_error
from bes.common.inspect_util import inspect_util

class git_repo_document_db(object):
  'Store and update a text document in a git repository.'

  def __init__(self, working_dir, repo_address, branch):
    root_dir = path.join(working_dir, git_address_util.sanitize_for_local_path(repo_address), branch)
    self.repo = git_repo(root_dir, repo_address)
    self.repo.clone_or_pull()
    self.repo.checkout(branch)

  def update_document(self, filename, update_func, commit_msg, codec = 'utf-8'):
    """
    Runs the update function (minimally 'lambda old_content: new_content') to update the document.
    Creates a file with the given name at the repo address that was provided on init.
    """
    check.check_function(update_func)
    # Getting this error: 'module' object has no attribute 'getfullargspec'
    #update_func_spec = inspect_util.getargspec(update_func)
    #if len(update_func_spec[0]) != 1:
    #  raise git_error('update_func should take exactly one argument.')

    def _git_update_op(repo):
      # This is called from operation_with_reset below.
      fp = repo.file_path(filename)
      first_time = not path.exists(fp)

      # This sets the content to '' the first time, but None would allow update_func to
      # distinguish the true first time from a later time where it happened to become empty. On the
      # other hand, None would make the update_func more complex if all you want to do is
      # concatenate.
      contents = '' if first_time else file_util.read(fp, codec = codec)

      updated_contents = update_func(contents)
      file_util.save(fp, updated_contents, codec = codec)
      if first_time:
        # Stage the new file.
        repo.add([filename])
      # Upon return from this function, operation_with_reset will attempt a git
      # commit and push. If it fails, it will do a hard reset of the repo
      # (which will remove any staged file) and call this again.

    self.repo.operation_with_reset(_git_update_op, commit_msg)

  def load_document(self, filename, codec = 'utf-8'):
    'Returns the content from the repo for the filename.'
    self.repo.reset_to_revision('@{upstream}')
    self.repo.pull()
    fp = self.repo.file_path(filename)
    return file_util.read(fp, codec = codec)
