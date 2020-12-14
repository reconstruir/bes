#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.common.check import check
from bes.fs.file_util import file_util

from .git_repo_document_db import git_repo_document_db

class git_repo_document_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(clazz, command)
    return func(**kargs)
  
  @classmethod
  def update_document(clazz, input_filename, address, branch, working_dir, commit_msg):
    # For the purposes of this CLI, the name of the stored file in the repo will be the same as the
    # base name of the file used to provide the source document contents.
    filename = path.basename(input_filename)
    db = git_repo_document_db(working_dir, address, branch)
    new_contents = file_util.read(input_filename)
    if not commit_msg:
      commit_msg = 'git_repo_document_db commit'

    # For the purposes of this CLI, just throw away the old contents. There's no way to update them.
    db.update_document(filename, lambda old_contents: new_contents, commit_msg)

    return 0

  @classmethod
  def load_document(clazz, filename, address, branch, output_filename, working_dir):
    db = git_repo_document_db(working_dir, address, branch)
    if not output_filename:
      output_filename = path.join(os.getcwd(), filename)
    content = db.load_document(filename)
    file_util.save(output_filename, content)
    return 0
