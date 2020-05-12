# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re, pprint, time
from datetime import datetime
from collections import namedtuple

from bes.archive.archiver import archiver
from bes.common.check import check
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.fs.dir_util import dir_util
from bes.fs.file_copy import file_copy
from bes.fs.file_ignore import ignore_file_data
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.log import logger
from bes.text.text_line_parser import text_line_parser
from bes.version.software_version import software_version

from .git_address_util import git_address_util
from .git_branch import git_branch
from .git_branch_list import git_branch_list
from .git_changelog import git_changelog
from .git_clone_options import git_clone_options
from .git_commit_hash import git_commit_hash
from .git_config import git_config
from .git_error import git_error
from .git_exe import git_exe
from .git_head_info import git_head_info
from .git_modules_file import git_modules_file
from .git_status import git_status
from .git_submodule_info import git_submodule_info

class git(object):
  'A class to deal with git.'

  log = logger('git')

  @classmethod
  def status(clazz, root, filenames, abspath = False, untracked_files = True):
    filenames = object_util.listify(filenames)
    flags = [ '--porcelain' ]
    if untracked_files:
      flags.append('--untracked-files=normal')
    else:
      flags.append('--untracked-files=no')
    args = [ 'status' ] + flags + filenames
    rv = git_exe.call_git(root, args)
    result = git_status.parse(rv.stdout)
    if abspath:
      for r in result:
        r.filename = path.join(root, r.filename)
    return result

  @classmethod
  def branch_status(clazz, root):
    rv = git_exe.call_git(root, [ 'status', '-b', '--porcelain' ])
    return git_branch.parse_branch_status(rv.stdout)

  @classmethod
  def remote_update(clazz, root):
    return git_exe.call_git(root, [ 'remote', 'update' ])

  @classmethod
  def remote_origin_url(clazz, root):
    return clazz.remote_get_url(root, name = 'origin')

  @classmethod
  def remote_set_url(clazz, root, url, name = 'origin'):
    check.check_string(root)
    check.check_string(url)
    check.check_string(name)
    
    args = [ 'remote', 'set-url', name, url ]
    git_exe.call_git(root, args)

  @classmethod
  def remote_get_url(clazz, root, name = 'origin'):
    check.check_string(root)
    check.check_string(name)

    args = [ 'remote', 'get-url', name ]
    try:
      rv = git_exe.call_git(root, args)
      return rv.stdout.strip()
    except git_error as ex:
      return None
    
  @classmethod
  def has_changes(clazz, root, untracked_files = False):
    return clazz.status(root, '.', untracked_files = untracked_files) != []

  @classmethod
  def add(clazz, root, filenames):
    filenames = object_util.listify(filenames)
    args = [ 'add' ] + filenames
    return git_exe.call_git(root, args)

  @classmethod
  def move(clazz, root, src, dst):
    args = [ 'mv', src, dst ]
    return git_exe.call_git(root, args)

  @classmethod
  def init(clazz, root, *args):
    args = [ 'init', '.' ] + list(args or [])
    return git_exe.call_git(root, args)

  @classmethod
  def is_bare_repo(clazz, root):
    'Return True if d is a bare git repo meaning it has git files.'
    expected_files = [ 'HEAD', 'config', 'description', 'hooks', 'info', 'objects', 'refs' ]
    for f in expected_files:
      if not path.exists(path.join(root, f)):
        return False
    return True

  @classmethod
  def is_repo(clazz, root):
    'Return True if d is a git repo meaning it has a .git dir with git files.'
    dot_git_dir = path.join(root, '.git')
    return path.isdir(dot_git_dir) and clazz.is_bare_repo(dot_git_dir)

  @classmethod
  def check_is_repo(clazz, d):
    'Raise an error if d is not a valid git repo.'
    if not clazz.is_repo(d):
      raise git_error('Not a git repo: "{}"'.format(d))

  @classmethod
  def check_is_bare_repo(clazz, d):
    'Raise an error if d is not a valid bare repo.'
    if not clazz.is_bare_repo(d):
      raise git_error('Not a bare git repo: "{}"'.format(d))
    
  @classmethod
  def clone(clazz, address, dest_dir, options = None):
    check.check_git_clone_options(options, allow_none = True)
    address = git_address_util.resolve(address)
    options = options or git_clone_options()
    clazz.log.log_d('clone: address={} dest_dir={} options={}'.format(address, dest_dir, pprint.pformat(options.__dict__)))
    if path.exists(dest_dir):
      if not path.isdir(dest_dir):
        raise git_error('dest_dir "{}" is not a directory.'.format(dest_dir))
      if options.enforce_empty_dir:
        if not dir_util.is_empty(dest_dir):
          raise git_error('dest_dir "{}" is not empty.'.format(dest_dir))
    else:
      file_util.mkdir(dest_dir)
    args = [ 'clone' ]
    if options.depth:
      args.extend([ '--depth', str(options.depth) ])
    args.append(address)
    args.append(dest_dir)
    extra_env = {
      'GIT_LFS_SKIP_SMUDGE': '0' if options.lfs else '1',
    }
    clazz.log.log_d('clone: args="{}" extra_env={}'.format(' '.join(args), extra_env))
    clone_rv = git_exe.call_git(os.getcwd(), args, extra_env = extra_env)
    clazz.log.log_d('clone: clone_rv="{}"'.format(str(clone_rv)))
    sub_rv = None
    if options.branch:
      git.checkout(dest_dir, options.branch)
    if options.submodules or options.submodule_list:
      sub_rv = clazz._submodule_init(dest_dir, options)
    return clone_rv, sub_rv

  @classmethod
  def _submodule_init(clazz, dest_dir, options):
    assert options.submodules or options.submodule_list

    lfs_env = {
      'GIT_LFS_SKIP_SMUDGE': '0' if options.lfs else '1',
    }
    sub_args = [ 'submodule', 'update', '--init' ]
    if options.jobs:
      sub_args.extend([ '--jobs', str(options.jobs) ])
    if options.submodules_recursive:
      sub_args.append('--recursive')
    if options.submodule_list:
      sub_args.extend(options.submodule_list)
    clazz.log.log_d('_submodule_init: sub_args="{}" lfs_env={}'.format(' '.join(sub_args), lfs_env))
    sub_rv = git_exe.call_git(dest_dir, sub_args, extra_env = lfs_env)
    clazz.log.log_d('_submodule_init: sub_rv="{}"'.format(str(sub_rv)))
    return sub_rv
  
  @classmethod
  def sync(clazz, address, dest_dir, options = None):
    check.check_git_clone_options(options, allow_none = True)
    if clazz.is_repo(dest_dir):
      clazz.checkout(dest_dir, 'master')
    clazz.clone_or_pull(address, dest_dir, options = options)
    branches = clazz.list_branches(dest_dir, 'both')
    for needed_branch in branches.difference:
      clazz.branch_track(dest_dir, needed_branch)
    git_exe.call_git(dest_dir, 'fetch --all')
    git_exe.call_git(dest_dir, 'pull --all')

  @classmethod
  def pull(clazz, root, *args):
    args = [ 'pull', '--verbose' ] + list(args or [])
    return git_exe.call_git(root, args)

  @classmethod
  def checkout(clazz, root, revision):
    args = [ 'checkout', revision ]
    return git_exe.call_git(root, args)

  @classmethod
  def push(clazz, root, *args):
    args = [ 'push', '--verbose' ] + list(args or [])
    return git_exe.call_git(root, args)

  @classmethod
  def push_with_rebase(clazz, root, remote_name = None, num_tries = None, retry_wait_ms = None):
    'Push, but call "pull --rebase origin master" first to be up to date.  With multiple optional retries.'
    check.check_string(root)
    check.check_string(remote_name, allow_none = True)
    check.check_int(num_tries, allow_none = True)
    check.check_float(retry_wait_ms, allow_none = True)

    if check.is_int(num_tries):
      if num_tries <= 0 or num_tries > 100:
        raise ValueError('num_tries should be between 1 and 100: {}'.format(num_tries))

    num_tries = num_tries or 1
    save_ex = None
    origin = clazz.remote_origin_url(root) or '<unknown>'
    remote_name = remote_name or 'origin'
    active_branch = clazz.active_branch(root)
    retry_wait_ms = retry_wait_ms or 0.500

    pull_command = 'pull --rebase {} {}'.format(remote_name, active_branch)

    clazz.log.log_d('push_with_rebase: num_tries={} pull_command="{}" retry_wait_ms={}'.format(num_tries,
                                                                                               pull_command,
                                                                                               retry_wait_ms))
    for i in range(0, num_tries):
      try:
        clazz.log.log_d('push_with_rebase: attempt {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        git_exe.call_git(root, pull_command)
        clazz.push(root)
        clazz.log.log_i('push_with_rebase: success {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        return
      except git_error as ex:
        clazz.log.log_w('push_with_rebase: failed {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        time.sleep(retry_wait_ms)
        save_ex = ex
    raise save_ex

  @classmethod
  def diff(clazz, root):
    args = [ 'diff' ]
    return git_exe.call_git(root, args).stdout

  @classmethod
  def patch_apply(clazz, root, patch_file):
    args = [ 'apply', patch_file ]
    return git_exe.call_git(root, args)

  @classmethod
  def patch_make(clazz, root, patch_file):
    args = [ 'diff', '--patch' ]
    rv = git_exe.call_git(root, args)
    file_util.save(patch_file, content = rv.stdout)

  @classmethod
  def commit(clazz, root_dir, message, filenames):
    filenames = object_util.listify(filenames)
    message_filename = temp_file.make_temp_file(content = message)
    args = [ 'commit', '-F', message_filename ] + filenames
    rv = git_exe.call_git(root_dir, args)
    return clazz.last_commit_hash(root_dir, short_hash = True)

  @classmethod
  def clone_or_pull(clazz, address, dest_dir, options = None):
    options = options or git_clone_options()
    
    if clazz.is_repo(dest_dir):
      if options.reset_to_head:
        clazz.reset_to_revision(dest_dir, 'HEAD')

      if options.submodules or options.submodule_list:
        clazz._submodule_init(dest_dir, options)
        
      if clazz.has_changes(dest_dir):
        raise git_error('dest_dir "{}" has changes.'.format(dest_dir))

      info = clazz.head_info(dest_dir)

      if info.is_detached:
        clazz.checkout(dest_dir, 'master')

      if not options.no_network:
        git_exe.call_git(dest_dir, 'fetch --tags')
        clazz.pull(dest_dir)

      if options.branch:
        clazz.checkout(dest_dir, options.branch)
        if not options.no_network:
          clazz.pull(dest_dir)
    else:
      clazz.clone(address, dest_dir, options = options)

  @classmethod
  def archive(clazz, address, revision, base_name, output_filename, untracked = False):
    'git archive with additional support to include untracked files for local repos.'
    tmp_repo_dir = temp_file.make_temp_dir()
    if path.isdir(address):
      file_copy.copy_tree(address, tmp_repo_dir, excludes = clazz.read_gitignore(address))
      if untracked:
        git_exe.call_git(tmp_repo_dir, [ 'add', '-A' ])
        git_exe.call_git(tmp_repo_dir, [ 'commit', '-m', 'add untracked files just for tmp repo' ])
    else:
      if untracked:
        raise git_error('untracked can only be True for local repos.')
      clazz.clone(address, tmp_repo_dir)
    output_filename = path.abspath(output_filename)
    file_util.mkdir(path.dirname(output_filename))
    args = [
      'archive',
      '--format=tgz',
      '--prefix=%s-%s/' % (base_name, revision),
      '-o',
      output_filename,
      revision
    ]
    rv = git_exe.call_git(tmp_repo_dir, args)
    return rv

  @classmethod
  def archive_to_file(clazz, root, prefix, revision, output_filename,
                      archive_format = None, short_hash = True):
    'git archive with additional support to include untracked files for local repos.'
    prefix = file_util.ensure_rsep(prefix)
    archive_format = archive_format or 'tgz'
    output_filename = path.abspath(output_filename)
    file_util.ensure_file_dir(output_filename)
    if short_hash:
      if clazz.is_long_hash(revision):
        revision = clazz.short_hash(root, revision)

    args = [
      'archive',
      '--format={}'.format(archive_format),
      '--prefix={}'.format(prefix),
      '-o',
      output_filename,
      revision
    ]
    git_exe.call_git(root, args)

  @classmethod
  def archive_to_dir(clazz, root, revision, output_dir):
    'git archive to a dir.'
    file_util.mkdir(output_dir)
    tmp_archive = temp_file.make_temp_file(suffix = '.tar')
    args = [
      'archive',
      '--format=tar',
      '-o',
      tmp_archive,
      revision,
    ]
    git_exe.call_git(root, args)
    archiver.extract_all(tmp_archive, output_dir)

  @classmethod
  def short_hash(clazz, root, long_hash):
    args = [ 'rev-parse', '--short', long_hash ]
    rv = git_exe.call_git(root, args)
    return rv.stdout.strip()

  @classmethod
  def long_hash(clazz, root, short_hash):
    args = [ 'rev-parse', short_hash ]
    rv = git_exe.call_git(root, args)
    return rv.stdout.strip()

  @classmethod
  def reset(clazz, root, revision = None):
    args = [ 'reset', '--hard' ]
    if revision:
      args.append(revision)
    return git_exe.call_git(root, args)

  @classmethod
  def reset_to_revision(clazz, root, revision = None):
    return clazz.reset(root, revision = revision)

  @classmethod
  def revision_equals(clazz, root, revision1, revision2):
    'Return True if revision1 is the same as revision2.  Short and long hashes can be mixed.'
    revision1_long = clazz.long_hash(root, revision1)
    revision2_long = clazz.long_hash(root, revision2)
    return revision1_long == revision2_long

  @classmethod
  def last_commit_hash(clazz, root, short_hash = False):
    args = [ 'log', '--format=%H', '-n', '1' ]
    rv = git_exe.call_git(root, args)
    long_hash = rv.stdout.strip()
    if not short_hash:
      return long_hash
    return clazz.short_hash(root, long_hash)

  @classmethod
  def root(clazz, filename):
    'Return the repo root for the given filename or raise and exception if not under git control.'
    if path.isdir(filename):
      cwd = filename
    else:
      cwd = path.dirname(filename)
    args = [ 'rev-parse', '--show-toplevel' ]
    rv = git_exe.call_git(cwd, args, raise_error = False)
    if rv.exit_code != 0:
      return None
    l = clazz._parse_lines(rv.stdout)
    assert len(l) == 1
    return l[0]

  @classmethod
  def is_tracked(clazz, root, filename):
    'Return True if the filename is tracked by a git repo.'
    args = [ 'ls-files', '--error-unmatch', filename ]
    return git_exe.call_git(root, args, raise_error = False).exit_code == 0

  @classmethod
  def modified_files(clazz, root):
    items = clazz.status(root, '.')
    return [ item.filename for item in items if 'M' in item.action ]

  @classmethod
  def tag(clazz, root_dir, tag, allow_downgrade = False, push = False):
    greatest_tag = git.greatest_local_tag(root_dir)
    if greatest_tag and not allow_downgrade:
      if software_version.compare(greatest_tag, tag) >= 0:
        raise ValueError('new tag \"%s\" is older than \"%s\".  Use allow_downgrade to force it.' % (tag, greatest_tag))
    git_exe.call_git(root_dir, [ 'tag', tag ])
    if push:
      clazz.push_tag(root_dir, tag)

  @classmethod
  def push_tag(clazz, root, tag):
    git_exe.call_git(root, [ 'push', 'origin', tag ])

  @classmethod
  def delete_local_tag(clazz, root, tag):
    git_exe.call_git(root, [ 'tag', '--delete', tag ])

  @classmethod
  def delete_remote_tag(clazz, root, tag):
    git_exe.call_git(root, [ 'push', '--delete', 'origin', tag ])

  @classmethod
  def delete_tag(clazz, root, tag, where, dry_run):
    clazz.check_where(where)
    if where in [ 'local', 'both' ]:
      local_tags = git.list_local_tags(root)
      if tag in local_tags:
        if dry_run:
          print('would delete local tag \"{tag}\"'.format(tag = tag))
        else:
          clazz.delete_local_tag(root, tag)
    if where in [ 'remote', 'both' ]:
      remote_tags = git.list_remote_tags(root)
      if tag in remote_tags:
        if dry_run:
          print('would delete remote tag \"{tag}\"'.format(tag = tag))
        else:
          clazz.delete_remote_tag(root, tag)

  @classmethod
  def list_local_tags(clazz, root, lexical = False, reverse = False):
    if lexical:
      sort_arg = '--sort={reverse}refname'.format(reverse = '-' if reverse else '')
    else:
      sort_arg = '--sort={reverse}version:refname'.format(reverse = '-' if reverse else '')
    rv = git_exe.call_git(root, [ 'tag', '-l', sort_arg ])
    return clazz._parse_lines(rv.stdout)

  @classmethod
  def greatest_local_tag(clazz, root):
    tags = clazz.list_local_tags(root)
    if not tags:
      return None
    return tags[-1]

  @classmethod
  def list_remote_tags(clazz, root, lexical = False, reverse = False):
    rv = git_exe.call_git(root, [ 'ls-remote', '--tags' ])
    lines = clazz._parse_lines(rv.stdout)
    tags = [ clazz._parse_remote_tag_line(line) for line in lines ]
    if lexical:
      return sorted(tags, reverse = reverse)
    else:
      return software_version.sort_versions(tags, reverse = reverse)
    return tags

  @classmethod
  def greatest_remote_tag(clazz, root):
    tags = clazz.list_remote_tags(root)
    if not tags:
      return None
    return tags[-1]

  @classmethod
  def _parse_remote_tag_line(clazz, s):
    f = re.findall('^[0-9a-f]{40}\s+refs/tags/(.+)$', s)
    if f and len(f) == 1:
      return string_util.remove_tail(f[0], '^{}')
    return None

  @classmethod
  def _parse_lines(clazz, s):
    return text_line_parser.parse_lines(s, strip_comments = False, strip_text = True, remove_empties = True)

  @classmethod
  def commit_timestamp(clazz, root, commit):
    rv = git_exe.call_git(root, [ 'show', '-s', '--format=%ct', commit ])
    ts = float(rv.stdout.strip())
    return datetime.fromtimestamp(ts)

  @classmethod
  def commit_for_tag(clazz, root, tag, short_hash = False):
    args = [ 'rev-list', '-n', '1', tag ]
    rv = git_exe.call_git(root, args)
    long_hash = rv.stdout.strip()
    if not short_hash:
      return long_hash
    return clazz.short_hash(root, long_hash)

  @classmethod
  def commit_brief_message(clazz, root, commit_hash):
    args = [
      'log',
      '-n1',
      '--pretty=format:%s',
      commit_hash,
      '--',
    ]
    return git_exe.call_git(root, args).stdout.strip()

  @classmethod
  def read_gitignore(clazz, root):
    'Return the contents of .gitignore with comments stripped.'
    p = path.join(root, '.gitignore')
    if not path.isfile(p):
      return None
    return ignore_file_data.read_file(p).patterns

  @classmethod
  def config_set_value(clazz, key, value):
    git_config.set_value(key, value)

  @classmethod
  def config_unset_value(clazz, key):
    return git_config.unset_value(key)

  @classmethod
  def config_get_value(clazz, key):
    return git_config.get_value(key)

  @classmethod
  def config_set_identity(clazz, name, email):
    return git_config.set_identity(name, email)

  @classmethod
  def config_get_identity(clazz):
    return git_config.get_identity()

  _bump_tag_result = namedtuple('_bump_tag_result', 'old_tag, new_tag')
  @classmethod
  def bump_tag(clazz, root_dir, component, push = True, dry_run = False, default_tag = None, reset_lower = False):
    old_tag = git.greatest_local_tag(root_dir)
    if old_tag:
      new_tag = software_version.bump_version(old_tag, component, reset_lower = reset_lower)
    else:
      new_tag = default_tag or '1.0.0'
    if not dry_run:
      git.tag(root_dir, new_tag)
      if push:
        git.push_tag(root_dir, new_tag)
    return clazz._bump_tag_result(old_tag, new_tag)

  @classmethod
  def where_is_valid(clazz, where):
    return where in [ 'local', 'remote', 'both' ]

  @classmethod
  def check_where(clazz, where):
    if not clazz.where_is_valid(where):
      raise ValueError('where should be local, remote or both instead of: {}'.format(where))
    return where

  @classmethod
  def determine_where(clazz, local, remote, default_value = 'both'):
    if local is None and remote is None:
      return default_value
    local = bool(local)
    remote = bool(remote)
    if local and remote:
      return 'both'
    elif local:
      return 'local'
    elif remote:
      return 'remote'
    assert False

  @classmethod
  def active_branch(clazz, root):
    return [ i for i in clazz.list_branches(root, 'local') if i.active ][0].name

  @classmethod
  def list_branches(clazz, root, where):
    clazz.check_where(where)
    if where == 'local':
      branches = clazz.list_local_branches(root)
    elif where == 'remote':
      branches = clazz.list_remote_branches(root)
    else:
      branches = clazz._list_both_branches(root)
    return git_branch_list(branches)

  @classmethod
  def _branch_list_determine_authors(clazz, root, branches):
    result = git_branch_list()
    for branch in branches:
      result.append(branch.clone({ 'author': git.author(root, branch.commit, brief = True) }))
    return result

  @classmethod
  def list_remote_branches(clazz, root):
    rv = git_exe.call_git(root, [ 'branch', '--verbose', '--list', '--no-color', '--remote' ])
    lines = clazz._parse_lines(rv.stdout)
    lines = [ line for line in lines if not ' -> ' in line ]
    lines = [ string_util.remove_head(line, 'origin/') for line in lines ]
    branches = git_branch_list([ git_branch.parse_branch(line, 'remote') for line in lines ])
    return clazz._branch_list_determine_authors(root, branches)

  @classmethod
  def list_local_branches(clazz, root):
    rv = git_exe.call_git(root, [ 'branch', '--verbose', '--list', '--no-color' ])
    lines = clazz._parse_lines(rv.stdout)
    branches = git_branch_list([ git_branch.parse_branch(line, 'local') for line in lines ])
    return clazz._branch_list_determine_authors(root, branches)

  @classmethod
  def has_remote_branch(clazz, root, branch):
    return branch in clazz.list_remote_branches(root).names

  @classmethod
  def has_local_branch(clazz, root, branch):
    return branch in clazz.list_local_branches(root).names
  
  @classmethod
  def _list_both_branches(clazz, root):
    local_branches = clazz.list_local_branches(root)
    remote_branches = clazz.list_remote_branches(root)
    branch_map = {}

    for branch in clazz.list_remote_branches(root):
      branch_map[branch.name] = [ branch ]

    for branch in clazz.list_local_branches(root):
      existing_branch = branch_map.get(branch.name, None)
      if existing_branch:
        assert len(existing_branch) == 1
        if existing_branch[0].compare(branch, remote_only = True) == 0:
          new_branch = existing_branch[0].clone(mutations = { 'where': 'both', 'active': branch.active, 'ahead': branch.ahead, 'behind': branch.behind })
          branch_map[branch.name] = [ new_branch ]
        else:
          branch_map[branch.name].append(branch)
      else:
        branch_map[branch.name] = [ branch ]
    result = git_branch_list()
    for _, branches in branch_map.items():
      result.extend(branches)
    result.sort()
    return clazz._branch_list_determine_authors(root, result)

  @classmethod
  def branch_create(clazz, root, branch_name, checkout = False, push = False):
    branches = clazz.list_branches(root, 'both')
    if branches.has_remote(branch_name):
      raise ValueError('branch already exists remotely: {}'.format(branch_name))
    if branches.has_local(branch_name):
      raise ValueError('branch already exists locally: {}'.format(branch_name))
    git_exe.call_git(root, [ 'branch', branch_name ])
    if checkout:
      clazz.checkout(root, branch_name)
    if push:
      clazz.branch_push(root, branch_name)

  @classmethod
  def branch_push(clazz, root, branch_name):
    git_exe.call_git(root, [ 'push', '--set-upstream', 'origin', branch_name ])

  @classmethod
  def branch_track(clazz, root, branch_name):
    git_exe.call_git(root, [ 'branch', '--track', branch_name ])

  @classmethod
  def fetch(clazz, root):
    git_exe.call_git(root, [ 'fetch', '--all' ])

  @classmethod
  def author(clazz, root, commit, brief = False):
    rv = git_exe.call_git(root, [ 'show', '--no-patch', '--pretty=%ae', commit ])
    author = rv.stdout.strip()
    if brief:
      i = author.find('@')
      if i > 0:
        author = author[0:i]
        i = author.find('.')
        if i > 0:
          author = author[0:i]
    return author

  @classmethod
  def files_for_commit(clazz, root, commit):
    'Return a list of files affected by commit.'
    args = [ 'diff-tree', '--no-commit-id', '--name-only', '-r', commit ]
    rv = git_exe.call_git(root, args)
    return sorted(clazz._parse_lines(rv.stdout))

  @classmethod
  def is_long_hash(clazz, h):
    'Return True if h is a valid git long hash.'
    return git_commit_hash.is_long(h)

  @classmethod
  def is_short_hash(clazz, h):
    'Return True if h is a valid git short hash.'
    return git_commit_hash.is_short(h)

  @classmethod
  def is_hash(clazz, h):
    'Return True if h is a valid git short or long hash.'
    return git_commit_hash.is_valid(h)

  @classmethod
  def files(clazz, root):
    'Return a list of all the files in the repo.'
    rv = git_exe.call_git(root, [ 'ls-files' ])
    return sorted(clazz._parse_lines(rv.stdout))

  @classmethod
  def lfs_files(clazz, root):
    'Return a list of all the lfs files in the repo.'
    rv = git_exe.call_git(root, [ 'lfs', 'ls-files' ])
    return sorted(clazz._parse_lines(rv.stdout))

  @classmethod
  def _lfs_file_needs_smudge(clazz, filename):
    'Return True if filename needs smudge.'
    pass

  @classmethod
  def lfs_files_need_smudge(clazz, root):
    'Return a list of all the lfs files that need smudge.'
    files = clazz.files(root)
    lfs_files = clazz.lfs_files(root)
    to_check = set(files) & set(lfs_files)
    result = []

  @classmethod
  def lfs_pull(clazz, root):
    args = [ 'lfs', 'pull' ]
    return git_exe.call_git(root, args)

  @classmethod
  def lfs_track(clazz, root, pattern):
    args = [ 'lfs', 'track', pattern ]
    return git_exe.call_git(root, args)

  @classmethod
  def remove(clazz, root, filenames):
    filenames = object_util.listify(filenames)
    args = [ 'rm' ] + filenames
    return git_exe.call_git(root, args)

  @classmethod
  def unpushed_commits(clazz, root): # tested
    'Return a list of unpushed commits.'
    rv = git_exe.call_git(root, [ 'cherry' ])
    lines = clazz._parse_lines(rv.stdout)
    result = []
    for line in lines:
      x = re.findall('^\+\s([a-f0-9]+)$', line)
      if x and len(x) == 1:
        result.append(x[0])
    return result

  @classmethod
  def has_unpushed_commits(clazz, root):
    return len(clazz.unpushed_commits(root)) > 0

  @classmethod
  def submodule_init(clazz, root, submodule = None, recursive = False):
    args = [ 'submodule', 'update', '--init' ]
    if recursive:
      args.append('--recursive')
    if submodule:
      args.append(submodule)
    return git_exe.call_git(root, args)

  @classmethod
  def submodule_status_all(clazz, root, submodule = None): # nottested
    args = [ 'submodule', 'status' ]
    if submodule:
      args.append(submodule)
    rv = git_exe.call_git(root, args)
    lines = clazz._parse_lines(rv.stdout)
    result = [ git_submodule_info.parse(line) for line in lines ]
    return [ clazz._submodule_info_fill_fields(root, info) for info in result ]

  @classmethod
  def _submodule_info_fill_fields(clazz, root, info):
    submodule_root = path.join(root, info.name)
    revision_short = clazz.short_hash(submodule_root, info.revision_long)
    branch = git_modules_file.module_branch(root, info.name)
    return info.clone(mutations = { 'branch': branch, 'revision': revision_short })

  @classmethod
  def submodule_add(clazz, root, address, local_path):
    check.check_string(root)
    check.check_string(address)
    check.check_string(local_path)
    args = [ 'submodule', 'add', address, local_path ]
    git_exe.call_git(root, args)

  @classmethod
  def submodule_status_one(clazz, root, submodule):
    return clazz.submodule_status_all(root, submodule = submodule)[0]

  @classmethod
  def submodule_update_revision(clazz, root, module_name, revision):
    clazz.submodule_init(root, submodule = module_name, recursive = False)
    status = clazz.submodule_status_one(root, module_name)
    module_root = path.join(root, module_name)
    revision_long = clazz.long_hash(module_root, revision)
    if revision_long == status.revision_long:
      return False
    branch = status.branch or 'master'
    clazz.checkout(module_root, branch)
    clazz.pull(module_root, 'origin', branch)
    clazz.checkout(module_root, revision_long)
    clazz.add(root, module_name)
    return True

  @classmethod
  def has_remote_tag(clazz, root, tag):
    return tag in clazz.list_remote_tags(root)

  @classmethod
  def has_local_tag(clazz, root, tag):
    return tag in clazz.list_local_tags(root)

  @classmethod
  def has_commit(clazz, root, commit):
    args = [ 'cat-file', '-t', commit ]
    return git_exe.call_git(root, args, raise_error = False).exit_code == 0

  @classmethod
  def has_revision(clazz, root, revision):
    return clazz.has_local_tag(root, revision) or clazz.has_commit(root, revision)

  @classmethod
  def changelog(clazz, root, revision_since, revision_until):
    check.check_string(root)
    check.check_string(revision_since, allow_none=True)
    check.check_string(revision_until, allow_none=True)

    revision_since = revision_since if revision_since else 'origin'
    revision_until = revision_until if revision_until else 'HEAD'
    revisions_range = '{}..{}'.format(revision_since, revision_until)
    args = ['log', revisions_range]
    data = git_exe.call_git(root, args)
    changelog_string = data.stdout.strip()

    return git_changelog.convert_changelog_string(changelog_string)

  @classmethod
  def changelog_as_string(clazz, root, revision_since, revision_until, options):
    commit_info_data = clazz.changelog(root, revision_since, revision_until)
    return git_changelog.truncate_changelog(commit_info_data, options)

  @classmethod
  def clean(clazz, root, immaculate = True):
    '''Clean untracked stuff in the repo.
    If immaculate is True this will include untracked dirs as well as giving
    the -f (force) and -x (ignore .gitignore rules) for a really immaculate repo
    Optionally does the same treatment for all submodules.
    '''
    args = [ 'clean', '-f' ]
    if immaculate:
      args.extend([ '-d', '-x' ])
    git_exe.call_git(root, args)

  @classmethod
  def head_info(clazz, root):
    'Return information about the HEAD of the repo.'
    rv = git_exe.call_git(root, [ 'branch', '--verbose' ])
    return git_head_info.parse_head_info(rv.stdout)

  @classmethod
  def is_tag(clazz, root_dir, ref):
    'Return True if ref is a tag.'
    check.check_string(root_dir)
    check.check_string(ref)

    rv = git_exe.call_git(root_dir, [ 'show-ref', ref ], raise_error = False)
    return rv.exit_code == 0 and 'refs/tags/{}'.format(ref) in rv.stdout
