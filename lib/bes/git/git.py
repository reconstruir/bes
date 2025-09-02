# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re, time
from datetime import datetime
from collections import namedtuple
import tempfile

from bes.archive.archiver import archiver
from ..system.check import check
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.fs.dir_util import dir_util
from bes.fs.file_copy import file_copy
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.system.host import host
from bes.system.log import logger
from bes.version.software_version import software_version

from .git_address_util import git_address_util
from .git_branch import git_branch
from .git_branch_list import git_branch_list
from .git_changelog import git_changelog
from .git_clone_options import git_clone_options
from .git_commit_hash import git_commit_hash
from .git_commit_info import git_commit_info
from .git_config import git_config
from .git_error import git_error
from .git_exe import git_exe
from .git_head_info import git_head_info
from .git_ignore import git_ignore
from .git_lfs import git_lfs
from .git_modules_file import git_modules_file
from .git_ref import git_ref
from .git_ref_info import git_ref_info
from .git_ref_where import git_ref_where
from .git_status import git_status, git_status_list
from .git_submodule_info import git_submodule_info
from .git_tag_list import git_tag_list
from .git_tag_sort_type import git_tag_sort_type

class git(git_lfs):
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
    result = git_status_list.parse(rv.stdout)
    if abspath:
      result.become_absolute(root)
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
  def remote_set_url(clazz, root_dir, url, name = 'origin'):
    check.check_string(root_dir)
    check.check_string(url)
    check.check_string(name)

    current_remote_url = clazz.remote_get_url(root_dir, name = name)
    if current_remote_url == None:
      args = [ 'remote', 'add', name, url ]
      git_exe.call_git(root_dir, args)
    else:
      args = [ 'remote', 'set-url', name, url ]
      git_exe.call_git(root_dir, args)

  @classmethod
  def remote_get_url(clazz, root_dir, name = 'origin'):
    check.check_string(root_dir)
    check.check_string(name)

    args = [ 'remote', 'get-url', name ]
    try:
      rv = git_exe.call_git(root_dir, args)
      return rv.stdout.strip()
    except git_error as ex:
      return None
    
  @classmethod
  def has_changes(clazz, root_dir, untracked_files = False):
    return clazz.status(root_dir, '.', untracked_files = untracked_files) != []

  @classmethod
  def add(clazz, root_dir, filenames, force = False):
    filenames = object_util.listify(filenames)
    force_args = [ '--force' ] if force else []
    args = [ 'add' ] + force_args + filenames
    return git_exe.call_git(root_dir, args)

  @classmethod
  def move(clazz, root_dir, src, dst):
    args = [ 'mv', src, dst ]
    return git_exe.call_git(root_dir, args)

  @classmethod
  def init(clazz, root_dir, *args):
    args = [ 'init', '.' ] + list(args or [])
    return git_exe.call_git(root_dir, args)

  @classmethod
  def is_bare_repo(clazz, root_dir):
    'Return True if d is a bare git repo meaning it has git files.'
    expected_files = [ 'HEAD', 'config', 'description', 'hooks', 'info', 'objects', 'refs' ]
    for f in expected_files:
      if not path.exists(path.join(root_dir, f)):
        return False
    return True

  @classmethod
  def is_repo(clazz, root_dir):
    'Return True if d is a git repo meaning it has a .git dir with git files.'
    dot_git_dir = path.join(root_dir, '.git')
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
  def is_empty(clazz, root_dir):
    'Return True of repo is empty.'
    return not clazz.has_commits(root_dir) and clazz.list_branches(root_dir, 'local') == []

  @classmethod
  def has_commits(clazz, root_dir):
    'Return True of repo has commits.'
    rv = git_exe.call_git(root_dir, [ 'log' ], raise_error = False)
    if rv.succeeded:
      return True
    return 'does not have any commits' not in rv.stderr
  
  @classmethod
  def clone(clazz, address, root_dir, options = None):
    check.check_git_clone_options(options, allow_none = True)
    
    address = git_address_util.resolve(address)
    options = options or git_clone_options()
    clazz.log.log_d('clone: address={} root_dir={} options={}'.format(address, root_dir, options))
    
    if path.exists(root_dir):
      if not path.isdir(root_dir):
        raise git_error('root_dir "{}" is not a directory.'.format(root_dir))
      if options.enforce_empty_dir:
        if not dir_util.is_empty(root_dir):
          files = dir_util.list(root_dir, relative = True)
          sorted_files = sorted(files, key = lambda f: f.lower())
          printed_files = '\n  '.join(sorted_files).strip()
          raise git_error('root_dir "{}" is not empty:\n  {}\n'.format(root_dir, printed_files))
    else:
      file_util.mkdir(root_dir)
      
    args = [ 'clone' ]
    if options.depth:
      args.extend([ '--depth', str(options.depth) ])
    if options.jobs:
      args.extend([ '--jobs', str(options.jobs) ])
    if options.branch:
      args.extend([ '--branch', options.branch ])
    if options.submodules_recursive:
      args.extend([ '--recursive' ])
    if options.shallow_submodules:
      args.extend([ '--shallow-submodules' ])
    args.append(address)
    args.append(root_dir)
    extra_env = git_lfs.lfs_make_env(options.lfs)
    clazz.log.log_d('clone: args="{}" extra_env={}'.format(' '.join(args), extra_env))
    clone_rv = git_exe.call_git(os.getcwd(),
                                args,
                                extra_env = extra_env,
                                num_tries = options.num_tries,
                                retry_wait_seconds = options.retry_wait_seconds)
    clazz.log.log_d('clone: clone_rv="{}"'.format(str(clone_rv)))
    sub_rv = None
    if options.branch:
      git.checkout(root_dir, options.branch)
    if options.submodules or options.submodule_list:
      sub_rv = clazz._submodule_init(root_dir, options)
    return clone_rv, sub_rv

  @classmethod
  def _submodule_init(clazz, root_dir, options):
    assert options.submodules or options.submodule_list

    lfs_env = git_lfs.lfs_make_env(options.lfs)
    sub_args = [ 'submodule', 'update', '--init' ]
    if options.jobs:
      sub_args.extend([ '--jobs', str(options.jobs) ])
    if options.submodules_recursive:
      sub_args.append('--recursive')
    if options.submodule_list:
      sub_args.extend(options.submodule_list)
    clazz.log.log_d('_submodule_init: sub_args="{}" lfs_env={}'.format(' '.join(sub_args), lfs_env))
    sub_rv = git_exe.call_git(root_dir, sub_args, extra_env = lfs_env)
    clazz.log.log_d('_submodule_init: sub_rv="{}"'.format(str(sub_rv)))

    if options.submodule_list:
      submodule_to_reset = options.submodule_list
    else:
      submodule_to_reset = [ info.name for info in clazz.submodule_status_all(root_dir) ]

    for submodule in submodule_to_reset:
      submodule_root_dir = path.join(root_dir, submodule)
      if options.reset_to_head:
        clazz.reset_to_revision(submodule_root_dir, 'HEAD')
      if options.clean:
        clazz.clean(submodule_root_dir, immaculate = options.clean_immaculate)
    
    return sub_rv
  
  @classmethod
  def sync(clazz, address, root_dir, options = None):
    check.check_git_clone_options(options, allow_none = True)

    if clazz.is_repo(root_dir):
      clazz.checkout(root_dir, 'master')
    clazz.clone_or_pull(address, root_dir, options = options)
    branches = clazz.list_branches(root_dir, 'both')
    for needed_branch in branches.difference:
      clazz.branch_track(root_dir, needed_branch)
    git_exe.call_git(root_dir, 'fetch --all')
    git_exe.call_git(root_dir, 'pull --all')

  # FIXME: branch_name is for backwards compatiblity but it should be removed.
  @classmethod
  def pull(clazz, root_dir, remote_name = None, branch_name = None, options = None):
    check.check_string(root_dir)
    check.check_git_clone_options(options, allow_none = True)
    
    options = options or git_clone_options()
    branch_name = branch_name or options.branch
    clazz.log.log_d('pull: root_dir={} branch_name={} options={}'.format(root_dir, branch_name, options))

    args = []
    if remote_name:
      args.append(remote_name)

    if options.reset_to_head:
      clazz.reset_to_revision(root_dir, 'HEAD')

    if options.clean:
      clazz.clean(root_dir, immaculate = options.clean_immaculate)
        
    if options.submodules or options.submodule_list:
      clazz._submodule_init(root_dir, options)

    if clazz.has_changes(root_dir):
      status = git_exe.call_git(root_dir, [ 'status', '--porcelain' ]).stdout.strip()
      raise git_error('root_dir "{}" has changes:\n{}\n'.format(root_dir, status))

    info = clazz.head_info(root_dir)

    if branch_name:
      git_exe.call_git(root_dir, [ 'fetch', 'origin', branch_name ])

    if info.is_detached:
      clazz.checkout(root_dir, 'master')

    if not options.no_network:
      clazz.tags_fetch(root_dir, force = True)
      clazz._call_pull(root_dir, *args)

    if options.branch:
      clazz.checkout(root_dir, options.branch)
      if not options.no_network:
        clazz._call_pull(root_dir, *args)

  @classmethod
  def _call_pull(clazz, root_dir, *args):
    check.check_string(root_dir)
    
    args = [ 'pull', '--verbose' ] + list(args)
    git_exe.call_git(root_dir, args)
        
  @classmethod
  def checkout(clazz, root, revision):
    args = [ 'checkout', revision ]
    return git_exe.call_git(root, args)

  @classmethod
  def push(clazz, root, *args):
    args = [ 'push', '--verbose' ] + list(args or [])
    return git_exe.call_git(root, args)

  @classmethod
  def push_with_rebase(clazz, root, remote_name = None, num_tries = None, retry_wait_seconds = None):
    'Push, but call "pull --rebase origin master" first to be up to date.  With multiple optional retries.'
    check.check_string(root)
    check.check_string(remote_name, allow_none = True)
    check.check_int(num_tries, allow_none = True)
    check.check_float(retry_wait_seconds, allow_none = True)

    if num_tries != None:
      if num_tries <= 0 or num_tries > 100:
        raise git_error('num_tries should be between 1 and 100: {}'.format(num_tries))

    num_tries = num_tries or 1
    save_ex = None
    origin = clazz.remote_origin_url(root) or '<unknown>'
    remote_name = remote_name or 'origin'
    active_branch = clazz.active_branch(root)
    retry_wait_seconds = retry_wait_seconds or 0.500

    pull_command = 'pull --rebase {} {}'.format(remote_name, active_branch)

    clazz.log.log_d('push_with_rebase: num_tries={} pull_command="{}" retry_wait_seconds={}'.format(num_tries,
                                                                                               pull_command,
                                                                                               retry_wait_seconds))
    for i in range(0, num_tries):
      try:
        clazz.log.log_d('push_with_rebase: attempt {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        git_exe.call_git(root, pull_command)
        clazz.push(root)
        clazz.log.log_i('push_with_rebase: success {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        return
      except git_error as ex:
        clazz.log.log_w('push_with_rebase: failed {} of {} pushing to {}'.format(i + 1, num_tries, origin))
        time.sleep(retry_wait_seconds)
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
    tmp_msg = temp_file.make_temp_file(content = message)
    args = [ 'commit', '-F', tmp_msg ] + filenames
    try:
      rv = git_exe.call_git(root_dir, args)
    finally:
      file_util.remove(tmp_msg)
    return clazz.last_commit_hash(root_dir, short_hash = True)

  @classmethod
  def clone_or_pull(clazz, address, root_dir, options = None):
    check.check_string(root_dir)
    check.check_git_clone_options(options, allow_none = True)

    options = options or git_clone_options()
    clazz.log.log_d('clone_or_pull: address={} root_dir={} options={}'.format(address,
                                                                              root_dir,
                                                                              options))
    if clazz.is_repo(root_dir):
      clazz.pull(root_dir, options = options)
    else:
      clazz.clone(address, root_dir, options = options)

  @classmethod
  def archive(clazz, address, revision, base_name, output_filename,
              untracked = False, override_gitignore = None, debug = False):
    'git archive with additional support to include untracked files for local repos.'
    tmp_repo_dir = temp_file.make_temp_dir(delete = not debug)
    
    if path.isdir(address):
      excludes = git_ignore.read_gitignore_file(address)
      file_copy.copy_tree(address, tmp_repo_dir, excludes = excludes)
      if override_gitignore:
        file_util.save(path.join(address, '.gitignore'), content = override_gitignore)
      if untracked:
        git_exe.call_git(tmp_repo_dir, [ 'add', '-A' ])
        git_exe.call_git(tmp_repo_dir, [ 'commit', '-m', '"add untracked files just for tmp repo"' ])
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
    'git archive to a archive file.'
    prefix = file_util.ensure_rsep(prefix)
    archive_format = archive_format or 'tgz'
    output_filename = path.abspath(output_filename)
    file_util.ensure_file_dir(output_filename)
    if short_hash:
      if clazz.is_long_hash(revision):
        revision = clazz.short_hash(root, revision)
    clazz.log.log_d('archive_to_file: revision={} output_filename={} archive_format={}'.format(revision, output_filename, archive_format))
    tmp_dir = temp_file.make_temp_dir()
    clazz.archive_to_dir(root, revision, tmp_dir)
    archiver.create(output_filename, tmp_dir, base_dir = prefix, extension = archive_format)

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
    if rv.failed:
      return None
    l = git_exe.parse_lines(rv.stdout)
    assert len(l) == 1
    return l[0]

  @classmethod
  def is_tracked(clazz, root, filename):
    'Return True if the filename is tracked by a git repo.'
    args = [ 'ls-files', '--error-unmatch', filename ]
    return git_exe.call_git(root, args, raise_error = False).succeeded

  @classmethod
  def modified_files(clazz, root):
    items = clazz.status(root, '.')
    return [ item.filename for item in items if 'M' in item.action ]

  @classmethod
  def tag(clazz, root_dir, tag, allow_downgrade = False, push = False,
          commit = None, annotation = None):
    check.check_string(root_dir)
    check.check_string(tag)
    check.check_bool(allow_downgrade)
    check.check_bool(push)
    check.check_string(commit, allow_none = True)
    check.check_string(annotation, allow_none = True)

    if not allow_downgrade:
      greatest_tag = git.greatest_local_tag(root_dir)
      if greatest_tag:
        if software_version.compare(greatest_tag.name, tag) >= 0:
          raise ValueError('new tag \"{}\" is older than \"{}\".  Use allow_downgrade to force it.'.format(tag,
                                                                                                           greatest_tag.name))
    if not commit:
      commit = clazz.last_commit_hash(root_dir, short_hash = True)
    args = [ 'tag', tag, commit ]
    if annotation:
      args.append('--annotate')
      args.append('--message')
      args.append(string_util.quote(annotation))
    rv = git_exe.call_git(root_dir, args)
    if push:
      clazz.push_tag(root_dir, tag)

  @classmethod
  def tag_rename(clazz, root_dir, old_tag, new_tag, push = False):
    clazz.log.log_d('tag_rename: root_dir={} old_tag={} new_tag={} push={}'.format(root_dir,
                                                                                   old_tag,
                                                                                   new_tag,
                                                                                   push))
    if clazz.tag_has_annotation(root_dir, old_tag):
      annotation = clazz.tag_annotation(root_dir, old_tag)
    else:
      annotation = None
    clazz.tag(root_dir, new_tag, allow_downgrade = True, commit = old_tag, annotation = annotation)
    clazz.push_tag(root_dir, new_tag)
    clazz.delete_tag(root_dir, old_tag, 'both')
      
  @classmethod
  def push_tag(clazz, root_dir, tag):
    git_exe.call_git(root_dir, [ 'push', 'origin', tag ])

  @classmethod
  def tags_fetch(clazz, root_dir, force = False):
    args = [ 'fetch', '--tags' ]
    if force:
      args.append('--force')
    git_exe.call_git(root_dir, args)
    
  @classmethod
  def delete_local_tag(clazz, root_dir, tag):
    clazz.log.log_d('delete_local_tag: root_dir={} tag={}'.format(root_dir, tag))
    git_exe.call_git(root_dir, [ 'tag', '--delete', tag ])

  @classmethod
  def delete_remote_tag(clazz, root_dir, tag):
    clazz.log.log_d('delete_remote_tag: root_dir={} tag={}'.format(root_dir, tag))
    git_exe.call_git(root_dir, [ 'push', '--delete', 'origin', tag ])

  @classmethod
  def delete_tag(clazz, root_dir, tag, where, dry_run = False):
    git_ref_where.check_where(where)

    clazz.log.log_d('delete_tag: root_dir={} tag={} where={} dry_run={}'.format(root_dir,
                                                                                tag,
                                                                                where,
                                                                                dry_run))
    
    if where in ( 'local', 'both' ):
      if git.has_local_tag(root_dir, tag):
        if dry_run:
          print('DRY_RUN: would delete local tag \"{tag}\"'.format(tag = tag))
        else:
          clazz.delete_local_tag(root_dir, tag)
    if where in ( 'remote', 'both' ):
      if git.has_remote_tag(root_dir, tag):
        if dry_run:
          print('DRY_RUN: would delete remote tag \"{tag}\"'.format(tag = tag))
        else:
          clazz.delete_remote_tag(root_dir, tag)

  @classmethod
  def list_tags(clazz, root_dir, where = None, sort_type = None, reverse = False,
                limit = None, prefix = None):
    where = git_ref_where.check_where(where)
    if where == 'both':
      raise git_error('where needs to be "local" or "remote" only: {}'.format(where))
    sort_type = git_tag_sort_type.check_sort_type(sort_type)
    if where == 'local':
      tags = clazz.list_local_tags(root_dir,
                                   sort_type = sort_type,
                                   reverse = reverse,
                                   limit = limit,
                                   prefix = prefix)
    else:
      tags = clazz.list_remote_tags(root_dir,
                                   sort_type = sort_type,
                                   reverse = reverse,
                                   limit = limit,
                                   prefix = prefix)
    return tags
          
  @classmethod
  def list_local_tags(clazz, root_dir, sort_type = None, reverse = False,
                      limit = None, prefix = None):
    sort_type = git_tag_sort_type.check_sort_type(sort_type)
    rv = git_exe.call_git(root_dir, [ 'tag', '-l', '--format="%(objectname) %(refname)"' ])
    return git_tag_list.parse_show_ref_output(rv.stdout,
                                              sort_type = sort_type,
                                              reverse = reverse,
                                              limit = limit,
                                              prefix = prefix)
    
  @classmethod
  def greatest_local_tag(clazz, root, prefix = None):
    tags = clazz.list_local_tags(root, sort_type = 'version', prefix = prefix)
    if not tags:
      return None
    return tags[-1]

  @classmethod
  def list_remote_tags(clazz, root, sort_type = None, reverse = False,
                       limit = None, prefix = None):
    rv = git_exe.call_git(root, [ 'ls-remote', '--tags' ])
    clazz.log.log_d('list_remote_tags: stdout="{}"'.format(rv.stdout))
    return git_tag_list.parse_show_ref_output(rv.stdout,
                                              sort_type = sort_type,
                                              reverse = reverse,
                                              limit = limit,
                                              prefix = prefix)

  @classmethod
  def list_remote_tags_for_address(clazz, address, sort_type = None, reverse = False,
                                   limit = None, prefix = None):
    rv = git_exe.call_git(tempfile.gettempdir(), [ 'ls-remote', '--tags', address ])
    clazz.log.log_d('list_remote_tags_for_address: stdout="{}"'.format(rv.stdout))
    return git_tag_list.parse_show_ref_output(rv.stdout,
                                              sort_type = sort_type,
                                              reverse = reverse,
                                              limit = limit,
                                              prefix = prefix)
  
  @classmethod
  def greatest_remote_tag(clazz, root, prefix = None):
    tags = clazz.list_remote_tags(root, sort_type = 'version', prefix = prefix)
    if not tags:
      return None
    return tags[-1]

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
  def read_gitignore(clazz, root_dir):
    'Return the contents of .gitignore with comments stripped.'
    return git_ignore.read_gitignore_file(root_dir)

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
  def bump_tag(clazz, root_dir, component, push = True, dry_run = False,
               default_tag = None, reset_lower = False, prefix = None):
    default_tag = default_tag or '1.0.0'
    old_tag = git.greatest_local_tag(root_dir, prefix = prefix)
    if old_tag:
      old_tag_name = old_tag.name
      new_tag_name = software_version.bump_version(old_tag.name, component, reset_lower = reset_lower)
    else:
      old_tag_name = None
      if prefix:
        new_tag_name = '{}{}'.format(prefix, default_tag)
      else:
        new_tag_name = default_tag
        
    if not dry_run:
      git.tag(root_dir, new_tag_name, allow_downgrade = prefix != None)
      if push:
        git.push_tag(root_dir, new_tag_name)
    return clazz._bump_tag_result(old_tag_name, new_tag_name)

  @classmethod
  def active_branch(clazz, root):
    branches = clazz.list_branches(root, 'local')
    for branch in branches:
      if branch.active:
        return branch.name
    return None

  @classmethod
  def list_branches(clazz, root, where, limit = None):
    check.check_string(root)
    where = git_ref_where.check_where(where)
    check.check_int(limit, allow_none = True)
    
    if where == 'local':
      branches = clazz.list_local_branches(root, limit = limit)
    elif where == 'remote':
      branches = clazz.list_remote_branches(root, limit = limit)
    else:
      branches = clazz._list_both_branches(root, limit = limit)
    return git_branch_list(branches)

  @classmethod
  def _branch_list_determine_authors(clazz, root, branches):
    result = git_branch_list()
    for branch in branches:
      result.append(branch.clone({ 'author': git.author(root, branch.commit, brief = True) }))
    return result

  @classmethod
  def list_remote_branches(clazz, root, limit = None):
    check.check_string(root)
    check.check_int(limit, allow_none = True)
    
    rv = git_exe.call_git(root, [ 'branch', '--verbose', '--list', '--no-color', '--remote' ])
    lines = git_exe.parse_lines(rv.stdout)
    lines = [ line for line in lines if not ' -> ' in line ]
    lines = [ string_util.remove_head(line, 'origin/') for line in lines ]
    branches = git_branch_list([ git_branch.parse_branch(line, 'remote') for line in lines ])
    branches = clazz._branch_list_determine_authors(root, branches)
    if limit != None:
      branches = branches[0:limit]
    return branches

  @classmethod
  def list_local_branches(clazz, root, limit = None):
    check.check_string(root)
    check.check_int(limit, allow_none = True)

    rv = git_exe.call_git(root, [ 'branch', '--verbose', '--list', '--no-color' ])
    lines = git_exe.parse_lines(rv.stdout)
    branches = git_branch_list([ git_branch.parse_branch(line, 'local') for line in lines ])
    branches = clazz._branch_list_determine_authors(root, branches)
    if limit != None:
      branches = branches[0:limit]
    return branches

  @classmethod
  def has_remote_branch(clazz, root, branch):
    return branch in clazz.list_remote_branches(root).names

  @classmethod
  def has_local_branch(clazz, root, branch):
    return branch in clazz.list_local_branches(root).names
  
  @classmethod
  def _list_both_branches(clazz, root, limit):
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
    result = clazz._branch_list_determine_authors(root, result)
    if limit != None:
      result = result[0:limit]
    return result

  @classmethod
  def branch_create(clazz, root, branch_name, checkout = False, push = False,
                    start_point = None):
    branches = clazz.list_branches(root, 'both')
    if branches.has_remote(branch_name):
      raise ValueError('branch already exists remotely: {}'.format(branch_name))
    if branches.has_local(branch_name):
      raise ValueError('branch already exists locally: {}'.format(branch_name))
    args = [ 'branch', branch_name ]
    if start_point:
      args.append(start_point)
    git_exe.call_git(root, args)
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
    return sorted(git_exe.parse_lines(rv.stdout))

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
    return sorted(git_exe.parse_lines(rv.stdout))

  @classmethod
  def remove(clazz, root, filenames):
    filenames = object_util.listify(filenames)
    args = [ 'rm' ] + filenames
    return git_exe.call_git(root, args)

  @classmethod
  def unpushed_commits(clazz, root_dir): # tested
    'Return a list of unpushed commits.'
    head_info = clazz.head_info(root_dir)
    if head_info.is_detached:
      rv = git_exe.call_git(root_dir, [ 'cherry', 'origin' ])
    else:
      rv = git_exe.call_git(root_dir, [ 'cherry' ])
    lines = git_exe.parse_lines(rv.stdout)
    result = []
    for line in lines:
      x = re.findall(r'^\+\s([a-f0-9]+)$', line)
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
    lines = git_exe.parse_lines(rv.stdout)
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

    # submodule urls that are local paths need to use unix like
    # separators even on windows.
    if path.exists(address):
      address = address.replace('\\', '/')
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
    branch_name = status.branch or 'master'
    clazz.checkout(module_root, branch_name)
    clazz.pull(module_root, remote_name = 'origin', branch_name = branch_name)
    clazz.checkout(module_root, revision_long)
    clazz.add(root, module_name)
    return True

  @classmethod
  def has_remote_tag(clazz, root_dir, tag):
    return clazz.list_remote_tags(root_dir).has_name(tag)

  @classmethod
  def has_local_tag(clazz, root_dir, tag):
    return clazz.list_local_tags(root_dir).has_name(tag)

  @classmethod
  def has_commit(clazz, root, commit):
    args = [ 'cat-file', '-t', commit ]
    return git_exe.call_git(root, args, raise_error = False).succeeded

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
    return git_head_info.parse_head_info(root, rv.stdout)

  @classmethod
  def ref_info(clazz, root_dir, ref_name):
    'Return information about a ref.'
    check.check_string(root_dir)
    check.check_string(ref_name)

    rv = git_exe.call_git(root_dir, [ 'show-ref', ref_name ])
    return git_ref_info.parse_show_ref_output(rv.stdout)
  
  @classmethod
  def is_tag(clazz, root_dir, ref_name):
    'Return True if ref is a tag.'
    check.check_string(root_dir)
    check.check_string(ref_name)

    try:
      return clazz.ref_info(root_dir, ref_name).is_tag
    except git_error as ex:
      return False

  @classmethod
  def tag_has_annotation(clazz, root_dir, tag_name):
    'Return True if tag_name has an annotation.'
    check.check_string(root_dir)
    check.check_string(tag_name)

    rv = git_exe.call_git(root_dir, [ 'cat-file', '-t', tag_name ])
    tag_type = rv.stdout.strip()
    assert tag_type in ( 'tag', 'commit' )
    return tag_type == 'tag'

  @classmethod
  def tag_annotation(clazz, root_dir, tag_name):
    'Return the annotation for tag_name or raise an error it is not annotated.'
    check.check_string(root_dir)
    check.check_string(tag_name)

    if not clazz.tag_has_annotation(root_dir, tag_name):
      raise git_error('not an annotated tag: "{}"'.format(tag_name))
    rv = git_exe.call_git(root_dir, [ 'tag', '-n', '--format=%(subject)', tag_name ])
    return string_util.unquote(rv.stdout.strip())

  @classmethod
  def is_branch(clazz, root_dir, ref_name):
    'Return True if ref is a branch.'
    check.check_string(root_dir)
    check.check_string(ref_name)

    try:
      return clazz.ref_info(root_dir, ref_name).is_branch
    except git_error as ex:
      return False

  @classmethod
  def branches_for_tag(clazz, root_dir, tag):
    return git_ref.branches_for_tag(root_dir, tag)

  @classmethod
  def branches_for_ref(clazz, root_dir, ref):
    return git_ref.branches_for_ref(root_dir, ref)

  @classmethod
  def find_root_dir(clazz, start_dir = None):
    '''
    Find the root dir of a git repo starting at start_dir.
    If start_dir is None then the current working directory is used
    Return the root dir if found or None if not.
    '''
    check.check_string(start_dir, allow_none = True)

    start_dir = start_dir or os.getcwd()
    rv = git_exe.call_git(start_dir, [ 'rev-parse', '--show-toplevel' ], raise_error = False)
    if rv.failed:
      return None
    result = rv.stdout.strip()
    if host.SYSTEM == host.WINDOWS:
      result = result.replace('/', os.sep)
    return result

  @classmethod
  def commit_message(clazz, root_dir, revision):
    'Return the commit message for a single revision'
    rv = git_exe.call_git(root_dir, 'log -n 1 --pretty=format:%s {}'.format(revision))
    return rv.stdout.strip()

  @classmethod
  def commit_info(clazz, root_dir, commit_hash):
    'Return the commit message for a single revision'
    rv = git_exe.call_git(root_dir, [ 'show', '--quiet', commit_hash ])
    return git_commit_info.parse_log_output(rv.stdout)

  @classmethod
  def check_ignore(clazz, root_dir, filename):
    'Return True if filename should be ignored by git.  filename can exist or not'
    rv = git_exe.call_git(root_dir, [ 'check-ignore', filename ], raise_error = False)
    return rv.succeeded
