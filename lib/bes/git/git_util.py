# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path
import copy
from collections import namedtuple

from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.object_util import object_util
from bes.compat.StringIO import StringIO
from bes.fs.file_find import file_find
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
  def name_from_address(clazz, address):
    address = git.resolve_address(address)
    if path.isdir(address):
      return path.basename(address)
    if not address.endswith('.git'):
      raise ValueError('not a git address: %s' % (address))
    buf = StringIO()
    for c in string_util.reverse(address):
      if c in ':/':
        break
      buf.write(c)
    last_part = string_util.reverse(buf.getvalue())
    return string_util.remove_tail(last_part, '.git')

  @classmethod
  def sanitize_address(clazz, address):
    'Return path for local tarball.'
    return string_util.replace(address, { ':': '_', '/': '_' })

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
                                retry_wait_ms = options.retry_wait_ms)

  @classmethod
  def find_root_dir(clazz, start_dir = None, working_dir = True):
    'Find the root of a git repo starting at start_dir or None if not found.'
    start_dir = start_dir or os.getcwd()
    git_dir = file_find.find_in_ancestors(start_dir, '.git')
    if not git_dir:
      return None
    if working_dir:
      return path.normpath(path.join(git_dir, path.pardir))
    return git_dir

  @classmethod
  def truncate_changelog(clazz, list_of_commit_info, max_chars=4000, revision_chars=7, balance=0.5):
    check.check_list(list_of_commit_info, entry_type=git_commit_info)
    check.check_int(max_chars)
    check.check_int(revision_chars)
    check.check_float(balance)

    if max_chars < 1:
      raise ValueError("max_chars argument can't be less than 1")
    if revision_chars < 1:
      raise ValueError("revision_chars argument can't be less than 1")
    if balance <= 0 or balance > 1:
      raise ValueError("balance argument value must be inside next range - (0, 1]")

    list_of_commit_info = copy.deepcopy(list_of_commit_info)
    result = '\n'.join(str(elem) for elem in list_of_commit_info)
    total_chars = len(result)

    if total_chars <= max_chars:
      return result

    drop_functions_and_additional_arg = (
      (clazz._drop_revisions, revision_chars),
      (clazz._drop_merge_commit_messages, None),
      (clazz._drop_commit_messages_and_lines, balance)
    )

    for drop_function, additional_arg in drop_functions_and_additional_arg:
      args = [list_of_commit_info, total_chars, max_chars]
      if additional_arg:
        args.append(additional_arg)

      is_finished, total_chars = drop_function(*args)
      if is_finished:
        return '\n'.join(str(elem) for elem in list_of_commit_info)

  @staticmethod
  def _drop_revisions(list_of_commit_info, total_chars, max_chars, limit):
    for commit_info in list_of_commit_info:
      start_length = len(commit_info.revision)
      commit_info.revision = commit_info.revision[:limit]
      total_chars -= start_length - limit

    is_finished = total_chars <= max_chars
    return is_finished, total_chars

  @staticmethod
  def _drop_merge_commit_messages(list_of_commit_info, total_chars, max_chars):
    list_of_commit_info = list_of_commit_info[::-1]

    for commit_info in list_of_commit_info:
      if commit_info.is_merge_commit():
        start_length = len(commit_info.message)
        commit_info.message = '[dropped]'
        total_chars -= start_length - len(commit_info.message)

        if total_chars <= max_chars:
          return True, total_chars

    return False, total_chars

  @staticmethod
  def _drop_commit_messages_and_lines(list_of_commit_info, total_chars, max_chars, balance):
    list_of_commit_info.reverse()

    while total_chars > max_chars:
      limit = int(len(list_of_commit_info) * balance) + 1
      for index, commit_info in enumerate(list_of_commit_info):
        if index == limit:
          break

        if commit_info.message != '[dropped]':
          start_length = len(commit_info.message)
          commit_info.message = '[dropped]'
          total_chars -= start_length - len(commit_info.message)

          if total_chars <= max_chars:
            list_of_commit_info.reverse()
            return True, total_chars

      index = 0
      length = len(list_of_commit_info)
      while index < length:
        if index == limit:
          break

        start_length = len(list_of_commit_info[0])
        total_chars -= start_length + 1

        if total_chars <= max_chars:
          list_of_commit_info[:index + 1] = []
          list_of_commit_info.reverse()
          return True, total_chars

        index += 1
      list_of_commit_info[:index + 1] = []

    raise Exception('algorith is invalid for this case')
