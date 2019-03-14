#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.fs import file_type, file_util, file_find, temp_file
from bes.fs.testing import temp_content
from bes.version.version_compare import version_compare

from .git import git

class repo(object):
  'A mini git repo abstraction.'

  def __init__(self, root, address = None):
    self.root = path.abspath(root)
    self.address = address
    
  def __str__(self):
    return '%s@%s' % (self.root, self.address)

  def has_changes(self):
    return git.has_changes(self.root)
  
  def clone_or_pull(self):
    return git.clone_or_pull(self.address, self.root)

  def clone(self):
    return git.clone(self.address, self.root)

  def init(self, *args):
    return git.init(self.root, *args)

  def add(self, filenames):
    return git.add(self.root, filenames)

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

  @classmethod
  def make_temp_repo(clazz, address = None, content = None, delete = True):
    tmp_dir = temp_file.make_temp_dir(delete = delete)
    r = repo(tmp_dir, address = address)
    r.init()
    if content:
      r.write_temp_content(content)
      r.add('.')
      r.commit('add temp content', '.')
    return r
  
  def find_all_files(self):
    #crit = [
    #  file_type_criteria(file_type.DIR | file_type.FILE | file_type.LINK),
    #]
    #ff = finder(self.root, criteria = crit, relative = True)
    #return [ f for f in ff.find() ]
    files = file_find.find(self.root, relative = True, file_type = file_find.FILE|file_find.LINK)
    files = [ f for f in files if not f.startswith('.git') ]
    return files

  def last_commit_hash(self, short_hash = False):
    return git.last_commit_hash(self.root, short_hash = short_hash)

  def remote_origin_url(self):
    return git.remote_origin_url(selfroot)

  def add_file(self, filename, content):
    p = path.join(self.root, filename)
    assert not path.isfile(p)
    file_util.save(p, content = content)
    self.add( [ filename ])
    self.commit('add %s' % (filename), [ filename ])

  def read_file(self, filename):
    return file_util.read(path.join(self.root, filename))

  def last_tag(self):
    return git.last_tag(self.root)

  def list_tags(self, lexical = False, reverse = False):
    return git.list_tags(self.root, lexical = lexical, reverse = reverse)

  def list_tags_gt(self, tag, lexical = False, reverse = False):
    'List tags greater than tag'
    tags = self.list_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if version_compare.compare(t, tag) > 0 ]
    
  def list_tags_ge(self, tag, lexical = False, reverse = False):
    'List tags greater or equal to tag'
    tags = self.list_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if version_compare.compare(t, tag) >= 0 ]
    
  def list_tags_le(self, tag, lexical = False, reverse = False):
    'List tags lesser or equal to tag'
    tags = self.list_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if version_compare.compare(t, tag) <= 0 ]
    
  def list_tags_lt(self, tag, lexical = False, reverse = False):
    'List tags lesser than tag'
    tags = self.list_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if version_compare.compare(t, tag) < 0 ]
    
  def list_remote_tags(self, lexical = False, reverse = False):
    return git.list_remote_tags(self.root, lexical = lexical, reverse = reverse)

  def list_remote_tags_gt(self, tag, lexical = False, reverse = False):
    'List tags greater than tag'
    tags = self.list_remote_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if version_compare.compare(t, tag) > 0 ]
    
  def list_remote_tags_ge(self, tag, lexical = False, reverse = False):
    'List tags greater or equal to tag'
    tags = self.list_remote_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if version_compare.compare(t, tag) >= 0 ]
    
  def list_remote_tags_le(self, tag, lexical = False, reverse = False):
    'List tags lesser or equal to tag'
    tags = self.list_remote_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if version_compare.compare(t, tag) <= 0 ]
    
  def list_remote_tags_lt(self, tag, lexical = False, reverse = False):
    'List tags lesser than tag'
    tags = self.list_remote_tags(lexical = lexical, reverse = reverse)
    return [ t for t in tags if version_compare.compare(t, tag) < 0 ]
  
  def tag(self, tag, allow_downgrade = True):
    git.tag(self.root, tag, allow_downgrade = allow_downgrade)

  def delete_tag(self, tag):
    git.delete_tag(self.root, tag)

  def delete_remote_tag(self, tag):
    git.delete_remote_tag(self.root, tag)

  def push_tag(self, tag):
    git.push_tag(self.root, tag)
    
  def bump_tag(self, component = 'revision', push = True, dry_run = False):
    git.bump_tag(self.root, component = component, push = push, dry_run = dry_run)
    
check.register_class(repo, name = 'git_repo')
