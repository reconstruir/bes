# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import copy
from collections import namedtuple

from ..system.check import check
from bes.common.string_util import string_util
from bes.common.object_util import object_util
from bes.fs.file_type import file_type
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.execute import execute
from bes.system.log import logger
from bes.script.blurber import blurber

from ..files.find.bf_file_finder import bf_file_finder
from ..files.find.bf_file_finder_options import bf_file_finder_options
from ..files.match.bf_file_matcher import bf_file_matcher

from .git import git
from .git_repo import git_repo
from .git_commit_info import git_commit_info
from .git_repo_script_options import git_repo_script_options
from .git_repo_operation_options import git_repo_operation_options

class git_util(object):
  'Some higher level git utilities.'

  _LOG = logger('git')

  @classmethod
  def find_git_dirs(clazz, dirs):
    'Return the first .git dir found in any dir in dirs.'
    matcher = bf_file_matcher()
    matcher.add_item_fnmatch('.git', path_type = 'basename')
    options = bf_file_finder_options(file_type = 'dir', file_matcher = matcher)
    finder = bf_file_finder(options = options)
    result = finder.find(dirs).absolute_filenames()
    result = [ file_util.remove_tail(d, '.git') for d in result ]
    return sorted(result)
  
  @classmethod
  def is_long_hash(clazz, h):
    'Return True if h is a long hash.'
    return git.is_long_hash(h)

  @classmethod
  def is_short_hash(clazz, h):
    'Return True if h is a short hash.'
    return git.is_short_hash(h)

  @classmethod
  def repo_greatest_tag(clazz, address):
    'Return the greatest numeric tag of a git project by address.'
    repo = clazz.clone_to_temp_dir(address)
    greatest_tag = repo.greatest_local_tag()
    file_util.remove(repo.root)
    return greatest_tag

  @classmethod
  def repo_bump_tag(clazz, address, component, dry_run, reset_lower = False):
    'Bump the tag of a repo by address.'
    repo = clazz.clone_to_temp_dir(address)
    result = repo.bump_tag(component, push = True, dry_run = dry_run, reset_lower = reset_lower)
    file_util.remove(repo.root)
    return result

  @classmethod
  def clone_to_temp_dir(clazz, address, options = None, debug = False):
    'Clone a git address to a temp dir'
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    clazz._LOG.log_d('clone_to_temp_dir: tmp_dir={}'.format(tmp_dir))
    if debug:
      print('clone_to_temp_dir: tmp_dir={}'.format(tmp_dir))
    repo = git_repo(tmp_dir, address = address)
    repo.clone(options = options)
    assert repo.root == tmp_dir
    return repo

  script = namedtuple('script', 'filename, args')
  _one_script_result = namedtuple('_one_script_result', 'script, stdout')
  _run_scripts_result = namedtuple('_run_scripts_result', 'results, status, diff')
  @classmethod
  def repo_run_scripts(clazz, address, scripts, options = None):
    check.check_git_repo_script_options(options, allow_none = True)
    options = options or git_repo_script_options()
    if options.verbose:
      print('repo_run_scripts: cloning {}'.format(address))
    repo = clazz.clone_to_temp_dir(address, options = options, debug = options.debug)
    if options.debug:
      msg = 'repo_run_scripts: repo.root={}'.format(repo.root)
      print(msg)
      clazz._LOG.log_d(msg)
    scripts_results = []
    for script in scripts:
      if not repo.has_file(script.filename):
        raise IOError('script not found in {}/{}'.format(address, script.filename))
      if options.dry_run:
        print('DRY_RUN: would run {}/{} {} push={}'.format(address, script.filename, script.args or '', options.push))
        scripts_results.append(None)
      else:
        cmd = [ script.filename ]
        if script.args:
          cmd.extend(script.args)
        clazz._LOG.log_d('repo_run_scripts: executing cmd="{}" root={}'.format(' '.join(cmd), repo.root))
        if options.verbose:
          print('repo_run_scripts: executing {} in cwd={}'.format(' '.join(cmd), repo.root))
        rv = execute.execute(cmd, cwd = repo.root, shell = True, stderr_to_stdout = True)
        clazz._LOG.log_d('repo_run_scripts: rv={}'.format(str(rv)))
        scripts_results.append(clazz._one_script_result(script, rv.stdout))
    if options.push:
      if options.dry_run:
        print('DRY_RUN: {}: would push'.format(address))
      else:
        if options.push_with_rebase:
          repo.push_with_rebase(num_tries = options.push_with_rebase_num_tries,
                                retry_wait_seconds = options.push_with_rebase_retry_wait_seconds)
        else:
          repo.push()
    if options.bump_tag_component is not None:
      if options.dry_run:
        rv = repo.bump_tag(options.bump_tag_component, dry_run = True)
        print('DRY_RUN: {}: would bump "{}" component of tag {} to {}'.format(address, options.bump_tag_component, rv.old_tag, rv.new_tag))
      else:
        repo.bump_tag(options.bump_tag_component, push = True)
    result = clazz._run_scripts_result(scripts_results, repo.call_git([ 'status', '.' ]).stdout, repo.diff())
    file_util.remove(repo.root)
    return result

  @classmethod
  def repo_run_operation(clazz, address, operation, commit_message, options = None):
    check.check_string(address)
    check.check_callable(operation)
    check.check_string(commit_message)
    check.check_git_repo_operation_options(options, allow_none = True)

    options = options or git_repo_operation_options()
    if options.verbose:
      print('repo_run_operation: cloning {}'.format(address))
    repo = clazz.clone_to_temp_dir(address, options = options, debug = options.debug)
    if options.debug:
      msg = 'repo_run_operation: repo.root={}'.format(repo.root)
      print(msg)
      clazz._LOG.log_d(msg)
    if options.dry_run:
      print('DRY_RUN: would execute {} on {} in {}'.format(operation, address, repo.root))
    else:
      if options.verbose:
        print('repo_run_operation: executing {} in cwd={}'.format(operation, repo.root))
      repo.operation_with_reset(operation,
                                commit_message,
                                num_tries = options.num_tries,
                                retry_wait_seconds = options.retry_wait_seconds,
                                files_to_commit = options.files_to_commit)
    file_util.remove(repo.root)

  @classmethod
  def repo_update_submodule(clazz, address, submodule, branch, revision, dry_run, blurber = None):
    '''
    Update the submodule of git repo given by address to point to branch and revision
    '''
    check.check_string(address)
    check.check_string(submodule)
    check.check_string(branch)
    check.check_string(revision)
    check.check_bool(dry_run)
    check.check_blurber(blurber, allow_none = True)
    
    def _op(repo):
      repo.submodule_init(submodule = submodule, recursive = False)
      status = repo.submodule_status_one(submodule)
      old_revision = status.revision
      old_branch = status.branch
      if repo.is_long_hash(revision):
        new_revision = repo.short_hash(revision)
      else:
        new_revision = revision
      new_branch = branch
      msg = 'update {} from {}@{} to {}@{}'.format(submodule,
                                                   old_branch,
                                                   old_revision,
                                                   new_branch,
                                                   new_revision)
      repo.submodule_set_branch(submodule, branch)
      repo.submodule_update_revision(submodule, revision)
      if repo.has_changes():
        if blurber:
          blurber.blurb_verbose(msg)
        status = repo.status('.')
        changed_filenames = [ item.filename for item in status ]
        repo.add(changed_filenames)
        repo.commit(msg, changed_filenames)
      else:
        if blurber:
          blurber.blurb_verbose('nothing to change')
        
    options = git_repo_operation_options(dry_run = dry_run,
                                         branch = branch)
    # the commit happens inside the op which is the only place we have
    # all the data needed to compose it.
    msg = ''
    clazz.repo_run_operation(address, _op, msg, options = options)
      
