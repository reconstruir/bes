# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import atexit, inspect, time
import os.path as path

from bes.common.check import check
from bes.common.object_util import object_util
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.fs.testing.temp_content import temp_content
from bes.version.software_version import software_version

from .git import git
from .git_modules_file import git_modules_file

import warnings
with warnings.catch_warnings():
  warnings.filterwarnings("ignore", category = DeprecationWarning)
    
class git_repo(object):
  'A git repo abstraction.'

  def __init__(self, root, address = None):
    self.root = path.abspath(root)
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

  def add(self, filenames):
    return git.add(self.root, filenames)

  def remove(self, filenames):
    return git.remove(self.root, filenames)

  def pull(self):
    return git.pull(self.root)

  def push(self, *args):
    return git.push(self.root, *args)

  def push_with_rebase(self, remote_name = None, num_tries = None, retry_wait_ms = None):
    return git.push_with_rebase(self.root,
                                remote_name = remote_name,
                                num_tries = num_tries,
                                retry_wait_ms = retry_wait_ms)

  def safe_push(self, *args):
    return git.safe_push(self.root, *args)

  def commit(self, message, filenames):
    return git.commit(self.root, message, filenames)

  def checkout(self, revision):
    return git.checkout(self.root, revision)

  def status(self, filenames):
    return git.status(self.root, filenames)

  def diff(self):
    return git.diff(self.root)

  def exists(self):
    return path.isdir(self._dot_git_path())

  def branch_status(self):
    return git.branch_status(self.root)

  def write_temp_content(self, items, commit = False):
    temp_content.write_items(items, self.root)
    if commit:
      if self.has_changes():
        raise RuntimeError('You need a clean tree with no changes to add temp content.')
      self.add('.')
      self.commit('add temp content', '.')

  def _dot_git_path(self):
    return path.join(self.root, '.git')

  def find_all_files(self):
    files = file_find.find(self.root, relative = True, file_type = file_find.FILE|file_find.LINK)
    is_git = lambda f: f.startswith('.git') or f.endswith('.git')
    files = [ f for f in files if not is_git(f) ]
    return files

  def last_commit_hash(self, short_hash = False):
    return git.last_commit_hash(self.root, short_hash = short_hash)

  def remote_origin_url(self):
    return git.remote_origin_url(self.root)

  def add_file(self, filename, content, codec = 'utf-8', mode = None, commit = True, push = False):
    p = self.file_path(filename)
    assert not path.isfile(p)
    file_util.save(p, content = content, codec = codec, mode = mode)
    self.add( [ filename ])
    result = None
    if commit:
      self.commit('add %s' % (filename), [ filename ])
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

  def greatest_local_tag(self):
    return git.greatest_local_tag(self.root)

  def greatest_remote_tag(self):
    return git.greatest_remote_tag(self.root)

  def list_local_tags(self, lexical = False, reverse = False):
    return git.list_local_tags(self.root, lexical = lexical, reverse = reverse)

  def list_local_tags_gt(self, tag, lexical = False, reverse = False):
    'List tags greater than tag'
    tags = self.list_local_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if software_version.compare(t, tag) > 0 ]

  def list_local_tags_ge(self, tag, lexical = False, reverse = False):
    'List tags greater or equal to tag'
    tags = self.list_local_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if software_version.compare(t, tag) >= 0 ]

  def list_local_tags_le(self, tag, lexical = False, reverse = False):
    'List tags lesser or equal to tag'
    tags = self.list_local_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if software_version.compare(t, tag) <= 0 ]

  def list_local_tags_lt(self, tag, lexical = False, reverse = False):
    'List tags lesser than tag'
    tags = self.list_local_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if software_version.compare(t, tag) < 0 ]

  def list_remote_tags(self, lexical = False, reverse = False):
    return git.list_remote_tags(self.root, lexical = lexical, reverse = reverse)

  def list_remote_tags_gt(self, tag, lexical = False, reverse = False):
    'List tags greater than tag'
    tags = self.list_remote_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if software_version.compare(t, tag) > 0 ]

  def list_remote_tags_ge(self, tag, lexical = False, reverse = False):
    'List tags greater or equal to tag'
    tags = self.list_remote_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if software_version.compare(t, tag) >= 0 ]

  def list_remote_tags_le(self, tag, lexical = False, reverse = False):
    'List tags lesser or equal to tag'
    tags = self.list_remote_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if software_version.compare(t, tag) <= 0 ]

  def list_remote_tags_lt(self, tag, lexical = False, reverse = False):
    'List tags lesser than tag'
    tags = self.list_remote_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if software_version.compare(t, tag) < 0 ]

  def tag(self, tag, allow_downgrade = True, push = False):
    git.tag(self.root, tag, allow_downgrade = allow_downgrade, push = push)

  def has_remote_tag(self, tag):
    return git.has_remote_tag(self.root, tag)

  def has_local_tag(self, tag):
    return git.has_local_tag(self.root, tag)

  def delete_local_tag(self, tag):
    git.delete_local_tag(self.root, tag)

  def delete_remote_tag(self, tag):
    git.delete_remote_tag(self.root, tag)

  def delete_tag(clazz, tag, where, dry_run):
    return git.delete_tag(self.root, tag, where, dry_run)

  def push_tag(self, tag):
    git.push_tag(self.root, tag)

  def bump_tag(self, component, push = True, dry_run = False, default_tag = None, reset_lower = False):
    return git.bump_tag(self.root, component, push = push, dry_run = dry_run,
                        default_tag = default_tag, reset_lower = reset_lower)

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

  def list_remote_branches(self):
    return git.list_remote_branches(self.root)

  def list_local_branches(self):
    return git.list_local_branches(self.root)
  
  def has_remote_branch(self, branch):
    return git.has_remote_branch(self.root, branch)

  def has_local_branch(self, branch):
    return git.has_local_branch(self.root, branch)

  def branch_create(self, branch_name, checkout = False, push = False):
    git.branch_create(self.root, branch_name, checkout = checkout, push = push)

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

  def lfs_files_need_smudge(self):
    return git.lfs_files_need_smudge(self.root)

  def call_git(self, args, raise_error = True, extra_env = None):
    return git.call_git(self.root, args, raise_error = raise_error, extra_env = extra_env)

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
    return git.is_long_hash(h)

  @classmethod
  def is_short_hash(clazz, h):
    return git.is_short_hash(h)

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

  def operation_with_reset(self, operation, commit_message, num_tries = None, retry_wait_ms = None):
    '''
    Attempt a git operation.  With multiple tries.  Reset the repo before each
    attempt.

    Commit the results of the operation with commit_message and
    push it upstream.

    operation should be a function that takes exactly one "repo" argument
    of type "git_repo"
    '''

    check.check_function(operation)
    check.check_string(commit_message)
    check.check_int(num_tries, allow_none = True)
    check.check_float(retry_wait_ms, allow_none = True)

    operation_spec = inspect.getargspec(operation)
    if len(operation_spec[0]) != 1:
      raise RuntimeError('operation should take exactly one argument.')

    if check.is_int(num_tries):
      if num_tries <= 0 or num_tries > 100:
        raise ValueError('num_tries should be between 1 and 100: {}'.format(num_tries))

    num_tries = num_tries or 10
    save_ex = None
    retry_wait_ms = retry_wait_ms or 0.500

    git.log.log_d('operation_with_reset: num_tries={} operation="{}" retry_wait_ms={}'.format(num_tries,
                                                                                              operation,
                                                                                              retry_wait_ms))
    for i in range(0, num_tries):
      try:
        git.log.log_d('operation_with_reset: reset: attempt {} of {}'.format(i + 1, num_tries))
        self.reset_to_revision('@{upstream}')
        git.log.log_d('operation_with_reset: pull: attempt {} of {}'.format(i + 1, num_tries))
        self.pull()
        git.log.log_d('operation_with_reset: calling operation(): attempt {} of {}'.format(i + 1, num_tries))
        operation(self)
        if self.has_changes():
          git.log.log_d('operation_with_reset: committing...: attempt {} of {}'.format(i + 1, num_tries))
          self.commit(commit_message, [ '.' ])
        git.log.log_i('operation_with_reset: success {} of {}'.format(i + 1, num_tries))
        if self.has_unpushed_commits():
          git.log.log_d('operation_with_reset: pushing...: attempt {} of {}'.format(i + 1, num_tries))
          self.push()
        else:
          git.log.log_w('operation_with_reset: nothing to push.')
        return
      except RuntimeError as ex:
        git.log.log_w('operation_with_reset: failed {} of {}'.format(i + 1, num_tries))
        # git.log.log_exception(ex, show_traceback = True)
        time.sleep(retry_wait_ms)
        save_ex = ex
    assert save_ex
    raise save_ex

  def changelog(self, revision_since, revision_until):
    return git.changelog(self.root, revision_since, revision_until)

  def changelog_as_string(self, revision_since, revision_until, max_chars=None, revision_chars=7, balance=0.5):
    return git.changelog_as_string(self.root, revision_since, revision_until, max_chars, revision_chars, balance)

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

check.register_class(git_repo)
