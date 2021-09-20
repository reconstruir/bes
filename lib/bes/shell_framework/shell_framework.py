#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.git.git_clone_manager import git_clone_manager
from bes.git.git_clone_options import git_clone_options
from bes.git.git_repo import git_repo
from bes.git.git_util import git_util
from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger
from bes.text.line_break import line_break

from .shell_framework_defaults import shell_framework_defaults

class shell_framework(object):

  _log = logger('shell_framework')

  LATEST_REVISION = 'latest'
  
  def __init__(self, options = None):
    check.check_shell_framework_options(options, allow_none = True)

    self._options = options or shell_framework_options()

  @cached_property
  def framework_dir(self):
    return path.join(self._options.dest_dir, self._options.framework_basename)

  @cached_property
  def revision_filename(self):
    return path.join(self._options.dest_dir, self._options.revision_basename)

  @cached_property
  def old_revision(self):
    if not path.exists(self.revision_filename):
      return None
    if not path.isfile(self.revision_filename):
      raise IOError('Not a file: "{}"'.format(self.revision_filename))
    return file_util.read(self.revision_filename, codec = 'utf-8').strip()

  @cached_property
  def latest_revision(self):
    tag = git_util.repo_greatest_tag(self._options.address)
    if not tag:
      return None
    return tag.name
  
  @cached_property
  def new_revision(self):
    if self._options.revision == self.LATEST_REVISION:
      return self.latest_revision
    else:
      return self._options.revision
  
  def update(self):
    self._log.log_d('           address: {}'.format(self._options.address))
    self._log.log_d('framework_basename: {}'.format(self._options.framework_basename))
    self._log.log_d('     framework_dir: {}'.format(self.framework_dir))
    self._log.log_d(' revision_basename: {}'.format(self._options.revision_basename))
    self._log.log_d(' revision_filename: {}'.format(self.revision_filename))
    self._log.log_d('      old_revision: {}'.format(self.old_revision))
    self._log.log_d('      new_revision: {}'.format(self.new_revision))
      
    if self.old_revision == self.new_revision:
      self._log.log_d('already at revision: {}'.format(self.new_revision))
      return False
    
    self._fetch_framework()
    self._save_revision_filename()
    return True

  def _save_revision_filename(self):
    file_util.save(self.revision_filename, self.new_revision.strip() + line_break.DEFAULT_LINE_BREAK)
  
  def _fetch_framework(self):
    tmp_dir = temp_file.make_temp_dir(prefix = path.basename(self.framework_dir),
                                      dir = path.join(self.framework_dir, os.pardir),
                                      delete = False)
    options = git_clone_options(depth = 1,
                                num_tries = 3,
                                retry_wait_seconds = 5,
                                branch = self.new_revision)
    repo = git_repo(tmp_dir, address = self._options.address)
    repo.clone(options = options)
    file_util.remove(self.framework_dir)
    file_util.rename(tmp_dir, self.framework_dir)
