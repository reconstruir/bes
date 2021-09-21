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
from .shell_framework_options import shell_framework_options

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

  @property
  def current_revision(self):
    if not path.exists(self.revision_filename):
      return None
    if not path.isfile(self.revision_filename):
      raise IOError('Not a file: "{}"'.format(self.revision_filename))
    return file_util.read(self.revision_filename, codec = 'utf-8').strip()

  @property
  def latest_revision(self):
    tag = git_util.repo_greatest_tag(self._options.address)
    if not tag:
      return None
    return tag.name
  
  def _resolve_revision(self, revision):
    if revision == self.LATEST_REVISION:
      return self.latest_revision
    else:
      return revision
  
  def update(self, revision):
    check.check_string(revision)

    resolved_revision = self._resolve_revision(revision)
    self._log.log_d('           address: {}'.format(self._options.address))
    self._log.log_d('framework_basename: {}'.format(self._options.framework_basename))
    self._log.log_d('     framework_dir: {}'.format(self.framework_dir))
    self._log.log_d(' revision_basename: {}'.format(self._options.revision_basename))
    self._log.log_d(' revision_filename: {}'.format(self.revision_filename))
    self._log.log_d('  current_revision: {}'.format(self.current_revision))
    self._log.log_d('          revision: {}'.format(revision))
    self._log.log_d(' resolved_revision: {}'.format(resolved_revision))
      
    if self.current_revision == resolved_revision:
      self._log.log_d('already at revision: {}'.format(resolved_revision))
      return False
    
    self._fetch_framework(resolved_revision)
    self._save_revision_filename(resolved_revision)
    return True

  def _save_revision_filename(self, revision):
    file_util.save(self.revision_filename, revision.strip() + line_break.DEFAULT_LINE_BREAK)
  
  def _fetch_framework(self, revision):
    assert revision != 'latest'
    
    tmp_dir = temp_file.make_temp_dir(prefix = path.basename(self.framework_dir),
                                      dir = path.normpath(path.join(self.framework_dir, path.pardir)),
                                      delete = False)
    options = git_clone_options(depth = 1,
                                num_tries = 3,
                                retry_wait_seconds = 5,
                                branch = revision)
    repo = git_repo(tmp_dir, address = self._options.address)
    repo.clone(options = options)
    file_util.remove(self.framework_dir)
    src_dir = path.join(tmp_dir, 'bash', 'bes_shell')
    file_util.rename(src_dir, self.framework_dir)
    file_util.remove(tmp_dir)

  @classmethod
  def ensure(self, dest_dir, revision, address = None, framework_basename = None, revision_basename = None):
    check.check_string(dest_dir)
    check.check_string(revision)

    options = shell_framework_options()
    options.dest_dir = dest_dir
    if address:
      options.address = address
    if framework_basename:
      options.framework_basename = framework_basename
    if revision_basename:
      options.revision_basename = revision_basename
    framework = shell_framework(options = options)
    framework.update(revision)
