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
    dirs = object_util.listify(dirs)
    dirs = [ d for d in dirs if path.isdir(d) ]
    possible = []
    result = clazz._find(dirs, '.git', None, None, False)
    result = [ file_util.remove_tail(d, '.git') for d in result ]
    return sorted(result)

  @classmethod
  def _find(clazz, files, name, ft, max_depth, quit):
    if ft:
      ft = file_type.validate_file_type(ft)
    for f in files:
      if path.isdir(f):
        ff = clazz._make_finder(f, name, ft, max_depth, quit)
        for f in ff.find():
          yield f

  @classmethod
  def _make_finder(clazz, d, name, ft, max_depth, quit):
    crit_list = []
    if max_depth:
      crit_list.append(max_depth_criteria(max_depth))
    if name:
      if quit:
        action = criteria.STOP
      else:
        action = criteria.FILTER
      crit_list.append(pattern_criteria(name, action = action))
    if ft:
      crit_list.append(file_type_criteria(ft))
    return finder(d, criteria = crit_list)

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
    tmp_dir, repo = clazz._clone_to_temp_dir(address)
    greatest_tag = repo.greatest_local_tag()
    file_util.remove(tmp_dir)
    return greatest_tag

  @classmethod
  def repo_bump_tag(clazz, address, component, dry_run, reset_lower = False):
    'Bump the tag of a repo by address.'
    tmp_dir, repo = clazz._clone_to_temp_dir(address)
    result = repo.bump_tag(component, push = True, dry_run = dry_run, reset_lower = reset_lower)
    file_util.remove(tmp_dir)
    return result

  @classmethod
  def _clone_to_temp_dir(clazz, address, options = None, debug = False):
    'Clone a git address to a temp dir'
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    clazz._LOG.log_d('_clone_to_temp_dir: tmp_dir={}'.format(tmp_dir))
    if debug:
      print('_clone_to_temp_dir: tmp_dir={}'.format(tmp_dir))
    r = git_repo(tmp_dir, address = address)
    r.clone(options = options)
    return tmp_dir, r

  script = namedtuple('script', 'filename, args')
  _one_script_result = namedtuple('_one_script_result', 'script, stdout')
  _run_scripts_result = namedtuple('_run_scripts_result', 'results, status, diff')
  @classmethod
  def repo_run_scripts(clazz, address, scripts, options = None):
    check.check_git_repo_script_options(options, allow_none = True)
    options = options or git_repo_script_options()
    if options.verbose:
      print('repo_run_scripts: cloning {}'.format(address))
    tmp_dir, repo = clazz._clone_to_temp_dir(address, options = options, debug = options.debug)
    if options.debug:
      msg = 'repo_run_scripts: tmp_dir={} repo.root={}'.format(tmp_dir, repo.root)
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
                                retry_wait_ms = options.push_with_rebase_retry_wait_ms)
        else:
          repo.push()
    if options.bump_tag_component is not None:
      if options.dry_run:
        rv = repo.bump_tag(options.bump_tag_component, dry_run = True)
        print('DRY_RUN: {}: would bump "{}" component of tag {} to {}'.format(address, options.bump_tag_component, rv.old_tag, rv.new_tag))
      else:
        repo.bump_tag(options.bump_tag_component, push = True)
    return clazz._run_scripts_result(scripts_results, repo.call_git([ 'status', '.' ]).stdout, repo.diff())

  @classmethod
  def repo_run_operation(clazz, address, operation, commit_message, options = None):
    check.check_string(address)
    check.check_function(operation)
    check.check_string(commit_message)
    check.check_git_repo_operation_options(options, allow_none = True)

    options = options or git_repo_operation_options()
    if options.verbose:
      print('repo_run_operation: cloning {}'.format(address))
    tmp_dir, repo = clazz._clone_to_temp_dir(address, options = options, debug = options.debug)
    if options.debug:
      msg = 'repo_run_operation: tmp_dir={} repo.root={}'.format(tmp_dir, repo.root)
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
                                retry_wait_ms = options.retry_wait_ms,
                                files_to_commit = options.files_to_commit)
