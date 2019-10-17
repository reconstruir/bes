#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common.check import check
from bes.fs.file_type import file_type
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.fs.testing.temp_content import temp_content
from bes.version.software_version import software_version

from .git import git

class git_repo(object):
  'A mini git repo abstraction.'

  def __init__(self, root, address = None):
    self.root = path.abspath(root)
    self.address = address
    
  def __str__(self):
    return '%s@%s' % (self.root, self.address)

  def has_changes(self):
    return git.has_changes(self.root)
  
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
    files = [ f for f in files if not f.startswith('.git') ]
    return files

  def last_commit_hash(self, short_hash = False):
    return git.last_commit_hash(self.root, short_hash = short_hash)

  def remote_origin_url(self):
    return git.remote_origin_url(selfroot)

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

  def save_file(self, filename, content, codec = 'utf-8', mode = None):
    if not self.has_file(filename):
      self.add_file(filename, content, codec = codec, mode = mode)
      return
    p = self.file_path(filename)
    file_util.save(p, content = content, mode = mode)
    self.commit('modify %s' % (filename), [ filename ])
  
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
    return tag in self.list_remote_tags()

  def has_local_tag(self, tag):
    return tag in self.list_local_tags()

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

  def reset_to_revision(self, revision):
    git.reset_to_revision(self.root, revision)
  
  def list_branches(self, where):
    return git.list_branches(self.root, where)

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

  def submodule_init(self, submodule = None, recursive = False):
    return git.submodule_init(self.root, submodule = submodule, recursive = recursive)

  def submodule_status_all(self, submodule = None):
    return git.submodule_status_all(self.root, submodule = submodule)
  
  def submodule_status_one(self, submodule):
    return git.submodule_status_one(self.root, submodule)
  
check.register_class(git_repo)
