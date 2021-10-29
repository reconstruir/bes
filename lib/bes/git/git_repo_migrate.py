# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import copy
from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.object_util import object_util
from bes.fs.file_type import file_type
from bes.fs.file_util import file_util
from bes.fs.find.criteria import criteria
from bes.fs.find.file_type_criteria import file_type_criteria
from bes.fs.find.finder import finder
from bes.fs.find.max_depth_criteria import max_depth_criteria
from bes.fs.find.pattern_criteria import pattern_criteria
from bes.fs.temp_file import temp_file
from bes.system.execute import execute
from bes.system.log import logger
from bes.script.blurber import blurber

from .git import git
from .git_repo import git_repo
from .git_exe import git_exe
from .git_commit_info import git_commit_info
from .git_repo_migrate_options import git_repo_migrate_options

class git_repo_migrate(object):
  'Class to deal with migrating git repos from one remote to another.'

  _log = logger('git')

  @classmethod
  def migrate(clazz, old_address, new_address, options = None):
    check.check_string(old_address)
    check.check_string(new_address)
    check.check_git_repo_migrate_options(options, allow_none = True)
    options = options or git_repo_migrate_options()

    tmp_dir = temp_file.make_temp_dir(delete = not options.debug)
    old_dir = path.join(tmp_dir, 'old')
    new_dir = path.join(tmp_dir, 'new')

    self._log.log_d('options: {}'.format(options))
    self._log.log_d('old_dir: {}'.format(old_dir))
    self._log.log_d('new_dir: {}'.format(new_dir))
    return
    #clone --mirror git@gitlab_rebuilder:rebuilder/rem_health.git
    old_clone_args = [ 'clone', old_address, old_dir ]
    print(old_clone_args)
    git_exe.call_git('/tmp', old_clone_args)

    return
    old_repo = git_repo(old_dir, address = old_address)
    new_repo = git_repo(new_dir, address = new_address)

#    git.call_git(self, args, raise_error = True, extra_env = None,
#                 num_tries = None, retry_wait_seconds = None):
    
