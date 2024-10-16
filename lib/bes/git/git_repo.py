# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

import atexit
import os
import time

from ..system.check import check
from bes.common.inspect_util import inspect_util
from bes.common.object_util import object_util
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content
from bes.text.line_break import line_break
from bes.version.software_version import software_version

from ..files.bf_file_type import bf_file_type
from ..files.find.bf_file_finder import bf_file_finder
from ..files.match.bf_file_matcher import bf_file_matcher

from .git import git
from .git_address_util import git_address_util
from .git_commit_hash import git_commit_hash
from .git_error import git_error
from .git_exe import git_exe
from .git_modules_file import git_modules_file
from .git_operation_base import git_operation_base
from .git_repo_status import git_repo_status
from .git_repo_status_options import git_repo_status_options
from .git_tag_list import git_tag_list

#import warnings
#with warnings.catch_warnings():
#  warnings.filterwarnings("ignore", category = DeprecationWarning)
    
class git_repo(object):
  'A git repo abstraction.'

  def __init__(self, root, address = None, find_root = False):
    if find_root:
      found_root = git.find_root_dir(path.abspath(root))
    else:
      found_root = path.abspath(root)
    self.root = found_root
    self.address = address or git.remote_origin_url(self.root)

  def __str__(self):
    return '%s@%s' % (self.root, self.address)

  def has_changes(self, untracked_files = False, submodules = False):
    if git.has_changes(self.root, untracked_files = untracked_files):
      return True
    if submodules:
      for st in self.submodule_status_all():
        sub_repo = self.submodule_repo(st.name)
        if sub_repo.has_changes(untracked_files = untracked_files):
          return True
    return False

  def clone_or_pull(self, options = None):
    return git.clone_or_pull(self.address, self.root, options = options)

  def clone(self, options = None):
    return git.clone(self.address, self.root, options = options)

  def sync(self, options = None):
    return git.sync(self.address, self.root, options = options)

  def init(self, *args):
    return git.init(self.root, *args)

  def add(self, filenames, force = False):
    return git.add(self.root, filenames, force = force)

  def remove(self, filenames):
    return git.remove(self.root, filenames)

  def pull(self, remote_name = None, branch_name = None, options = None):
    return git.pull(self.root, remote_name = remote_name, branch_name = branch_name, options = options)

  def push(self, *args):
    return git.push(self.root, *args)

  def push_with_rebase(self, remote_name = None, num_tries = None, retry_wait_seconds = None):
    return git.push_with_rebase(self.root,
                                remote_name = remote_name,
                                num_tries = num_tries,
                                retry_wait_seconds = retry_wait_seconds)

  def safe_push(self, *args):
    return git.safe_push(self.root, *args)

  def commit(self, message, filenames):
    return git.commit(self.root, message, filenames)

  def checkout(self, revision):
    return git.checkout(self.root, revision)

  def status(self, filenames):
    return git.status(self.root, filenames)

  def status_as_string(self, filenames):
    return os.linesep.join([ str(st) for st in self.status(filenames) ])
  
  def diff(self):
    return git.diff(self.root)

  def exists(self):
    return path.isdir(self._dot_git_path())

  def branch_status(self):
    return git.branch_status(self.root)

  def write_temp_content(self, items, commit = False, commit_message = None):
    commit_message = commit_message or 'add temp content'
    temp_content.write_items(items, self.root)
    if commit:
      if self.has_changes():
        raise git_error('You need a clean tree with no changes to add temp content.')
      self.add('.')
      self.commit(commit_message, '.')
#
  def _dot_git_path(self):
    return path.join(self.root, '.git')

  def find_all_files(self, file_type = bf_file_type.FILE_OR_LINK):
    # we dont want to include the files in the .git dir
    walk_dir_matcher = bf_file_matcher()
    walk_dir_matcher.add_item_fnmatch('.git',
                                      file_type = 'dir',
                                      path_type = 'basename',
                                      negate = True)
    # we need to ignore files such as "foo.git" which are submodule
    # "links"
    matcher = bf_file_matcher()
    matcher.add_item_fnmatch('.git',
                             file_type = 'any',
                             path_type = 'basename',
                             negate = True)
    entries = bf_file_finder.find_with_options(self.root,
                                               file_matcher = matcher,
                                               file_type = file_type,
                                               match_type = 'all',
                                               walk_dir_matcher = walk_dir_matcher)
    return entries.relative_filenames()
  
  def find_all_files_as_string(self, file_type = bf_file_type.FILE_OR_LINK):
    return os.linesep.join(self.find_all_files(file_type = file_type))
  
  def last_commit_hash(self, short_hash = False):
    return git.last_commit_hash(self.root, short_hash = short_hash)

  def remote_origin_url(self):
    return git.remote_origin_url(self.root)

  def remote_set_url(self, url, name = 'origin'):
    return git.remote_set_url(self.root, url, name = name)
    
  def remote_get_url(self, name = 'origin'):
    return git.remote_get_url(self.root, name = name)
    
  def add_file(self, filename, content, codec = 'utf-8', mode = None, commit = True, push = False,
               commit_message = None):
    p = self.file_path(filename)
    assert not path.isfile(p)
    file_util.save(p, content = content, codec = codec, mode = mode)
    self.add( [ filename ])
    result = None
    if commit:
      commit_message = commit_message or 'add {}'.format(filename)
      self.commit(commit_message, [ filename ])
      result = self.last_commit_hash(short_hash = True)
    if push:
      self.push()
    return result

  def save_file(self, filename, content, codec = 'utf-8', mode = None, add = True, commit = True):
    if add and not commit:
      raise ValueError('If add is True then commit should be True as well.')
    p = self.file_path(filename)
    file_util.save(p, content = content, mode = mode)
    if add:
      self.add([ filename ])
    if commit:
      msg = 'add or change {}'.format(filename)
      self.commit(msg, [ filename ])

  def read_file(self, filename, codec = 'utf-8'):
    return file_util.read(self.file_path(filename), codec = codec)

  def has_file(self, filename):
    return path.exists(self.file_path(filename))

  def file_path(self, filename):
    return path.join(self.root, filename)

  def greatest_local_tag(self, prefix = None):
    return git.greatest_local_tag(self.root, prefix = prefix)

  def greatest_remote_tag(self, prefix = None):
    return git.greatest_remote_tag(self.root, prefix = prefix)

  def list_tags(self, where = None, sort_type = None, reverse = False,
                limit = None, prefix = None):
    return git.list_tags(self.root, where = where, sort_type = sort_type, reverse = reverse,
                         limit = limit, prefix = prefix)
  
  def list_local_tags(self, sort_type = None, reverse = False,
                      limit = None, prefix = None):
    return git.list_local_tags(self.root, sort_type = sort_type, reverse = reverse,
                               limit = limit, prefix = prefix)

  def list_local_tags_gt(self, tag, sort_type = None, reverse = False, limit = None, prefix = None):
    'List tags greater than tag'
    tags = self.list_local_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    return git_tag_list([ t for t in tags if software_version.compare(t.name, tag) > 0 ])

  def list_local_tags_ge(self, tag, sort_type = None, reverse = False, limit = None, prefix = None):
    'List tags greater or equal to tag'
    tags = self.list_local_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    return git_tag_list([ t for t in tags if software_version.compare(t.name, tag) >= 0 ])

  def list_local_tags_le(self, tag, sort_type = None, reverse = False, limit = None, prefix = None):
    'List tags lesser or equal to tag'
    tags = self.list_local_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    return git_tag_list([ t for t in tags if software_version.compare(t.name, tag) <= 0 ])

  def list_local_tags_lt(self, tag, sort_type = None, reverse = False, limit = None, prefix = None):
    'List tags lesser than tag'
    tags = self.list_local_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    return git_tag_list([ t for t in tags if software_version.compare(t.name, tag) < 0 ])

  def list_remote_tags(self, sort_type = None, reverse = False, limit = None, prefix = None):
    return git.list_remote_tags(self.root, sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)

  def list_remote_tags_gt(self, tag, sort_type = None, reverse = False, limit = None, prefix = None):
    'List tags greater than tag'
    tags = self.list_remote_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    return git_tag_list([ t for t in tags if software_version.compare(t.name, tag) > 0 ])

  def list_remote_tags_ge(self, tag, sort_type = None, reverse = False, limit = None, prefix = None):
    'List tags greater or equal to tag'
    tags = self.list_remote_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    return git_tag_list([ t for t in tags if software_version.compare(t.name, tag) >= 0 ])

  def list_remote_tags_le(self, tag, sort_type = None, reverse = False, limit = None, prefix = None):
    'List tags lesser or equal to tag'
    tags = self.list_remote_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    return git_tag_list([ t for t in tags if software_version.compare(t.name, tag) <= 0 ])

  def list_remote_tags_lt(self, tag, sort_type = None, reverse = False, limit = None, prefix = None):
    'List tags lesser than tag'
    tags = self.list_remote_tags(sort_type = sort_type, reverse = reverse, limit = limit, prefix = prefix)
    return git_tag_list([ t for t in tags if software_version.compare(t.name, tag) < 0 ])

  def tag(self, tag, allow_downgrade = True, push = False, commit = None,
          annotation = None):
    git.tag(self.root, tag, allow_downgrade = allow_downgrade,
            push = push, annotation = annotation)

  def tag_rename(self, old_tag, new_tag, push = False):
    git.tag_rename(self.root, old_tag, new_tag, push = push)

  def tag_has_annotation(self, tag_name):
    return git.tag_has_annotation(self.root, tag_name)

  def tag_annotation(self, tag_name):
    return git.tag_annotation(self.root, tag_name)
    
  def has_remote_tag(self, tag):
    return git.has_remote_tag(self.root, tag)

  def has_local_tag(self, tag):
    return git.has_local_tag(self.root, tag)

  def delete_local_tag(self, tag):
    git.delete_local_tag(self.root, tag)

  def delete_remote_tag(self, tag):
    git.delete_remote_tag(self.root, tag)

  def delete_tag(self, tag, where, dry_run = False):
    return git.delete_tag(self.root, tag, where, dry_run = False)

  def push_tag(self, tag):
    git.push_tag(self.root, tag)

  def bump_tag(self, component, push = True, dry_run = False, default_tag = None,
               reset_lower = False, prefix = None):
    return git.bump_tag(self.root, component, push = push, dry_run = dry_run,
                        default_tag = default_tag, reset_lower = reset_lower, prefix = prefix)

  def reset(self, revision = None, submodules = False):
    git.reset(self.root, revision = revision)
    if submodules:
      for st in self.submodule_status_all():
        sub_repo = self.submodule_repo(st.name)
        sub_repo.reset(revision = revision)
      self.submodule_init()

  def reset_to_revision(self, revision):
    git.reset_to_revision(self.root, revision)

  def revision_equals(self, revision1, revision2):
    'Return True if revision1 is the same as revision2.  Short and long hashes can be mixed.'
    return git.revision_equals(self.root, revision1, revision2)

  def list_branches(self, where):
    return git.list_branches(self.root, where)

  def list_remote_branches(self, limit = None):
    return git.list_remote_branches(self.root, limit = limit)

  def list_local_branches(self, limit = None):
    return git.list_local_branches(self.root, limit = limit)
  
  def has_remote_branch(self, branch):
    return git.has_remote_branch(self.root, branch)

  def has_local_branch(self, branch):
    return git.has_local_branch(self.root, branch)

  def branch_create(self, branch_name, checkout = False, push = False, start_point = None):
    git.branch_create(self.root, branch_name, checkout = checkout, push = push, start_point = start_point)

  def branch_push(self, branch_name):
    git.branch_push(self.root, branch_name)

  def fetch(self):
    git.fetch(self.root)

  def author(self, commit):
    git.author(self.root, commit)

  def files_for_commit(self, commit):
    return git.files_for_commit(self.root, commit)

  def active_branch(self):
    return git.active_branch(self.root)

  def archive_to_file(self, prefix, revision, output_filename,
                      archive_format = None, short_hash = True):
    git.archive_to_file(self.root, prefix, revision, output_filename,
                        archive_format = archive_format,
                        short_hash = short_hash)

  def archive_to_dir(self, revision, output_dir):
    return git.archive_to_dir(self.root, revision, output_dir)

  def lfs_track(self, pattern):
    return git.lfs_track(self.root, pattern)

  def lfs_pull(self):
    return git.lfs_pull(self.root)

  def lfs_files(self):
    return git.lfs_files(self.root)

  def lfs_files_needing_smudge(self):
    return git.lfs_files_needing_smudge(self.root)

  def call_git(self, args, raise_error = True, extra_env = None,
               num_tries = None, retry_wait_seconds = None):
    return git_exe.call_git(self.root,
                            args,
                            raise_error = raise_error,
                            extra_env = extra_env,
                            num_tries = num_tries,
                            retry_wait_seconds = retry_wait_seconds)

  def unpushed_commits(self):
    return git.unpushed_commits(self.root)

  def has_unpushed_commits(self):
    return git.has_unpushed_commits(self.root)

  def has_commit(self, commit):
    return git.has_commit(self.root, commit)

  def has_revision(self, revision):
    return git.has_revision(self.root, revision)

  @classmethod
  def is_long_hash(clazz, h):
    return git_commit_hash.is_long(h)

  @classmethod
  def is_short_hash(clazz, h):
    return git_commit_hash.is_short(h)

  @classmethod
  def is_hash(clazz, h):
    return git_commit_hash.is_valid(h)

  def short_hash(self, long_hash):
    return git.short_hash(self.root, long_hash)

  def long_hash(self, short_hash):
    return git.long_hash(self.root, short_hash)

  def submodule_init(self, submodule = None, recursive = False):
    return git.submodule_init(self.root, submodule = submodule, recursive = recursive)

  def submodule_add(self, address, local_path):
    return git.submodule_add(self.root, address, local_path)

  def submodule_status_all(self, submodule = None):
    return git.submodule_status_all(self.root, submodule = submodule)

  def submodule_status_one(self, submodule):
    return git.submodule_status_one(self.root, submodule)

  def submodule_file(self):
    filename = path.join(self.root, '.gitmodules')
    if not path.isfile(filename):
      raise IOError('no modules file found: {}'.format(filename))
    return git_modules_file(filename)

  def submodule_repo(self, submodule):
    'Return a git_repo object for the given submodule.'
    return git_repo(path.join(self.root, submodule))

  def has_submodule(self, submodule):
    'Return True if this repo has submodule.'
    return submodule in set([ info.name for info in self.submodule_status_all() ])

  def submodule_set_branch(self, module_name, branch_name):
    check.check_string(module_name)
    check.check_string(branch_name)
    self.submodule_file().set_branch(module_name, branch_name)

  def submodule_get_branch(self, module_name):
    check.check_string(module_name)
    return self.submodule_file().get_branch(module_name)

  def submodule_update_revision(self, module_name, revision):
    check.check_string(module_name)
    check.check_string(revision)
    return git.submodule_update_revision(self.root, module_name, revision)

  def commit_for_tag(self, tag, short_hash = False):
    check.check_string(tag)
    check.check_bool(short_hash)
    return git.commit_for_tag(self.root, tag, short_hash = short_hash)

  def commit_brief_message(self, commit_hash):
    check.check_string(commit_hash)
    return git.commit_brief_message(self.root, commit_hash)

  def operation_with_reset(self,
                           operation,
                           commit_message,
                           num_tries = None,
                           retry_wait_seconds = None,
                           files_to_commit = None):
    '''
    Attempt a git operation.  With multiple tries.  Reset the repo before each
    attempt.

    Commit the results of the operation with commit_message and
    push it upstream.

    operation should be a function that takes exactly one "repo" argument
    of type "git_repo"
    '''

    if check.is_callable(operation):
      operation_spec = inspect_util.getargspec(operation)
      if len(operation_spec[0]) != 1:
        raise git_error('operation should take exactly one argument.')
    elif isinstance(operation, git_operation_base):
      pass
    elif check.is_seq(operation, git_operation_base):
      pass
    else:
      raise TypeError('operation should be one or more objects that implement the git_operation_base interface.')
      
    check.check_string(commit_message)
    check.check_int(num_tries, allow_none = True)
    check.check_float(retry_wait_seconds, allow_none = True)
    check.check_string_seq(files_to_commit, allow_none = True)

    if check.is_int(num_tries):
      if num_tries <= 0 or num_tries > 100:
        raise ValueError('num_tries should be between 1 and 100: {}'.format(num_tries))

    num_tries = num_tries or 10
    save_ex = None
    retry_wait_seconds = retry_wait_seconds or 0.500
    files_to_commit = files_to_commit or [ '.' ]
    
    git.log.log_d('operation_with_reset: num_tries={} operation="{}" retry_wait_seconds={}'.format(num_tries,
                                                                                                   operation,
                                                                                                   retry_wait_seconds))
    for i in range(0, num_tries):
      try:
        git.log.log_d('operation_with_reset: reset: attempt {} of {}'.format(i + 1, num_tries))
        self.reset_to_revision('@{upstream}')
        git.log.log_d('operation_with_reset: pull: attempt {} of {}'.format(i + 1, num_tries))
        self.pull()
        git.log.log_d('operation_with_reset: calling operation(): attempt {} of {}'.format(i + 1, num_tries))
        self._call_operation(operation)
        if self.has_changes():
          git.log.log_d('operation_with_reset: committing...: attempt {} of {}'.format(i + 1, num_tries))
          self.commit(commit_message, files_to_commit)
        git.log.log_i('operation_with_reset: success {} of {}'.format(i + 1, num_tries))
        if self.has_unpushed_commits():
          git.log.log_d('operation_with_reset: pushing...: attempt {} of {}'.format(i + 1, num_tries))
          self.push('-u', 'origin', self.active_branch())
        else:
          git.log.log_w('operation_with_reset: nothing to push.')
        return
      except git_error as ex:
        git.log.log_w('operation_with_reset: failed {} of {}'.format(i + 1, num_tries))
        # git.log.log_exception(ex, show_traceback = True)
        time.sleep(retry_wait_seconds)
        save_ex = ex
    assert save_ex
    raise save_ex

  def _call_operation(self, operation):
    if check.is_callable(operation):
      operation(self)
    elif isinstance(operation, git_operation_base):
      operation.run(self)
    elif check.is_seq(operation, git_operation_base):
      for op in operation:
        op.run(self)
    
  def changelog(self, revision_since, revision_until):
    return git.changelog(self.root, revision_since, revision_until)

  def changelog_as_string(self, revision_since, revision_until, options):
    return git.changelog_as_string(self.root, revision_since, revision_until, options)

  def clean(self, immaculate = True, submodules = False):
    '''Clean untracked stuff in the repo.
    If immaculate is True this will include untracked dirs as well as giving
    the -f (force) and -x (ignore .gitignore rules) for a really immaculate repo
    '''
    git.clean(self.root, immaculate = immaculate)
    if submodules:
      for st in self.submodule_status_all():
        sub_repo = self.submodule_repo(st.name)
        sub_repo.clean(immaculate = immaculate)

  def atexit_operations(self, operations):
    'When the process exists, run one or more operations on the repo.'
    operations = object_util.listify(operations)
    from bes.system.log import log
    def _do_ops(*args, **kargs):
      arg_repo = args[0]
      arg_operations = args[1]
      for op in arg_operations:
        op(arg_repo)
    atexit.register(_do_ops, self, operations)

  def reset_and_clean(self, immaculate = False, submodules = False):
    '''
    Reset and clean the repo optionaly making it immaculate
    and also giving submodules the same treatment.
    '''
    self.reset(submodules = submodules)
    self.clean(immaculate = immaculate, submodules = submodules)

  def atexit_reset(self, submodules = False, revision = None):
    'When the process exists, reset and clean the repo'
    def _op(repo):
      repo.reset(revision = None, submodules = submodules)
    self.atexit_operations(_op)

  def atexit_reset_and_clean(self, immaculate = False, submodules = False):
    'When the process exists, reset and clean the repo'
    def _op(repo):
      repo.reset_and_clean(immaculate = immaculate, submodules = submodules)
    self.atexit_operations(_op)

  def head_info(self):
    'Return information about the HEAD of the repo.'
    return git.head_info(self.root)

  def ref_info(self, ref_name):
    'Return information about a ref.'
    return git.ref_info(self.root, ref_name)
  
  def is_tag(self, ref):
    'Return True if ref is a tag.'
    return git.is_tag(self.root, ref)

  def is_branch(self, ref):
    'Return True if ref is a branch.'
    return git.is_branch(self.root, ref)

  def cached_archive_get(self, revision, cache_dir = None):
    if not self.address:
      raise git_error('cached_archive only works for repos cloned from a remote address.')
    if not self._cached_archive_revision_is_valid(revision):
      raise git_error('revision should be a valid tag or commit hash: ""'.format(revision))
      
    cache_dir = self._cached_archive_resolve_cache_dir(cache_dir = cache_dir)
    local_address_path = self._cached_archive_path_for_address(cache_dir, self.address)
    tarball_filename = '{}.tar.gz'.format(revision)
    tarball_path = path.join(local_address_path, tarball_filename)
    if path.exists(tarball_path):
      return tarball_path

    tmp_dir = temp_file.make_temp_dir()
    name = git_address_util.name(self.address)
    tmp_full_path = path.join(tmp_dir, tarball_filename)

    prefix = '{}-{}'.format(name, revision)
    self.archive_to_file(prefix, revision, tmp_full_path, archive_format = 'tar.gz', short_hash = True)
    file_util.rename(tmp_full_path, tarball_path)
    return tarball_path

  def cached_archive_contains(self, revision, cache_dir = None):
    'Return True if the tarball with address and revision is in the cache.'
    cache_dir = self._cached_archive_resolve_cache_dir(cache_dir = cache_dir)
    local_address_path = self._cached_archive_path_for_address(cache_dir, self.address)
    tarball_filename = '{}.tar.gz'.format(revision)
    tarball_path = path.join(local_address_path, tarball_filename)
    return path.exists(tarball_path)

  def _cached_archive_revision_is_valid(self, revision):
    'Return True if revision is something that support archive caching.  Either commit hash or tag.'
    if self.is_tag(revision):
      return True
    if git_commit_hash.is_valid(revision):
      return self.has_commit(revision)
    return False
  
  @classmethod
  def _cached_archive_resolve_cache_dir(clazz, cache_dir = None):
    cache_dir = cache_dir or path.expanduser('~/.bes_git/archives')
    return cache_dir
    
  @classmethod
  def _cached_archive_path_for_address(clazz, cache_dir, address):
    return path.join(cache_dir, git_address_util.sanitize_for_local_path(address))

  def branches_for_tag(self, tag):
    return git.branches_for_tag(self.root, tag)

  def files(self):
    return git.files(self.root)
  
  def rsync_dir(self, src_repo, src_dir, src_revision, dst_dir):
    check.check_git_repp(src_repo)
    check.check_string(src_dir)
    check.check_string(src_revision)
    check.check_string(dst_dir)

    src_path = src_repo.path(src_dir)
    dst_path = self.path(dst_dir)

  def tags_fetch(self, force = False):
    return git.tags_fetch(self.root, force = force)

  def commit_message(self, revision):
    return git.commit_message(self.root, revision)
  
  def commit_info(self, commit_hash):
    return git.commit_info(self.root, commit_hash)

  def is_empty(self):
    return git.is_empty(self.root)

  def has_commits(self):
    return git.has_commits(self.root)
  
  def repo_status(self, options = None):
    check.check_git_repo_status_options(options, allow_none = True)

    options = options or git_repo_status_options()

    change_status = self.status([ '.' ])

    if not options.show_untracked:
      change_status.remove_untracked()
      
    branch_status = self.branch_status()
    active_branch = self.active_branch()
    last_commit_hash = self.last_commit_hash(short_hash = options.short_hash)
    last_commit = self.commit_info(last_commit_hash)

    return git_repo_status(change_status,
                           branch_status,
                           active_branch,
                           last_commit)
    
check.register_class(git_repo, include_seq = True)

'''
  @classmethod
  def get_status(self, root_dir):
    'Get the repo status for one git project'
    status = git.status(git_dir, [ '.' ])
    last_commit_hash = git.last_commit_hash(git_dir, short_hash = True)
    if not no_remote:
      git.remote_update(git_dir)
    branch_status = git.branch_status(git_dir)
    if untracked:
      changes = status
    else:
      changes = [ item for item in status if '?' not in item.action ]
    result = {
      'git_dir': git_dir,
      'status': status,
      'last_commit': last_commit_hash,
      'branch_status': { 'ahead': branch_status.ahead, 'behind': branch_status.behind },
      'active_branch': git.active_branch(git_dir),
      'changes': changes,
      'remote_origin_url': git.remote_origin_url(git_dir),
    } 
    return result
'''
