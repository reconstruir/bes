#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
import os.path as path
import multiprocessing

from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.git.git import git
from bes.git.git_error import git_error
from bes.git.git_repo import git_repo
from bes.git.git_status import git_status
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_temp_home_func
from bes.git.git_operation_base import git_operation_base
from bes.system.env_override import env_override_temp_home_func
from bes.system.execute import execute
from bes.testing.unit_test import unit_test

class test_git_repo(unit_test):

  def _make_repo(self, remote = True, content = None, prefix = None, commit_message = None):
    return git_temp_repo(remote = remote, content = content, prefix = prefix,
                         debug = self.DEBUG, commit_message = commit_message)

  @git_temp_home_func()
  def test_init(self):
    r = self._make_repo(remote = False)
    self.assertEqual( [], r.status('.') )

  @git_temp_home_func()
  def test_exists_false(self):
    tmp_dir = temp_file.make_temp_dir()
    r = git_repo(tmp_dir)
    self.assertFalse( r.exists() )

  @git_temp_home_func()
  def test_exists_true(self):
    r = self._make_repo(remote = False)
    self.assertTrue( r.exists() )

  @git_temp_home_func()
  def test_add(self):
    r = self._make_repo(remote = False)
    r.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r.add('.')
    self.assertEqual( [
      git_status(git_status.ADDED, 'a/b/c/foo.txt'),
      git_status(git_status.ADDED, 'd/e/bar.txt'),
    ], r.status('.') )
    
  @git_temp_home_func()
  def test_commit(self):
    r = self._make_repo(remote = False)
    r.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r.add('.')
    self.assertEqual( [
      git_status(git_status.ADDED, 'a/b/c/foo.txt'),
      git_status(git_status.ADDED, 'd/e/bar.txt'),
    ], r.status('.') )
    r.commit('foo', '.')
    self.assertEqual( [], r.status('.') )

  @git_temp_home_func()
  def test_pull(self):
    r1 = self._make_repo(remote = False)
    r1.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r1.add('.')
    r1.commit('foo', '.')

    tmp_dir = temp_file.make_temp_dir()
    git.clone(r1.root, tmp_dir)
    r2 = git_repo(tmp_dir)
    self.assertEqual( [], r2.status('.') )

    r1.write_temp_content([ 'file new/stuff.txt "some stuff" 644' ])
    r1.add('new/stuff.txt')
    r1.commit('foo', 'new/stuff.txt')

    new_stuff_path = path.join(r2.root, 'new/stuff.txt')
    self.assertFalse( path.exists(new_stuff_path) )
    r2.pull()
    self.assertTrue( path.exists(new_stuff_path) )

  @git_temp_home_func()
  def test_pull2(self):
    r1 = self._make_repo(remote = False)
    r1.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r1.add('.')
    r1.commit('foo', '.')

    tmp_dir = temp_file.make_temp_dir()
    r2 = git_repo(tmp_dir, address = r1.root)
    r2.clone()
    r2.pull()
    self.assertEqual([ self.xp_path('a/b/c/foo.txt'), self.xp_path('d/e/bar.txt') ], r2.find_all_files() )

    r1.write_temp_content([
      'file kiwi.txt "kiwi" 644',
    ])
    r1.add('kiwi.txt')
    r1.commit('foo', 'kiwi.txt')
    r2.pull()
    self.assertEqual([ self.xp_path('a/b/c/foo.txt'), self.xp_path('d/e/bar.txt'), 'kiwi.txt' ], r2.find_all_files() )

  @git_temp_home_func()
  def test_clone_or_pull(self):
    r1 = self._make_repo(remote = False)
    r1.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r1.add('.')
    r1.commit('foo', '.')

    tmp_dir = temp_file.make_temp_dir()
    r2 = git_repo(tmp_dir, address = r1.root)
    r2.clone_or_pull()
    self.assertEqual([ self.xp_path('a/b/c/foo.txt'), self.xp_path('d/e/bar.txt')], r2.find_all_files() )

    r1.write_temp_content([
      'file kiwi.txt "kiwi" 644',
    ])
    r1.add('kiwi.txt')
    r1.commit('foo', 'kiwi.txt')
    r2.pull()
    self.assertEqual([ self.xp_path('a/b/c/foo.txt'), self.xp_path('d/e/bar.txt'), 'kiwi.txt' ], r2.find_all_files() )
    
  @git_temp_home_func()
  def test_find_all_files(self):
    r = self._make_repo(remote = False)
    self.assertEqual([], r.find_all_files() )
    r.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r.add('.')
    r.commit('foo', '.')
    self.assertEqual([ self.xp_path('a/b/c/foo.txt'), self.xp_path('d/e/bar.txt')], r.find_all_files() )
   
  @git_temp_home_func()
  def test_push(self):
    r1 = self._make_repo()
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo', r2.read_file('foo.txt', codec = 'utf8') )
    
  @git_temp_home_func()
  def test_delete_remote_tags(self):
    r1 = self._make_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('1.0.0')
    r1.push_tag('1.0.0')
    r1.tag('1.0.1')
    r1.push_tag('1.0.1')
    self.assertEqual( [ '1.0.0', '1.0.1' ], r2.list_remote_tags() )
    r1.delete_local_tag('1.0.1')
    r1.delete_remote_tag('1.0.1')
    self.assertEqual( [ '1.0.0' ], r2.list_remote_tags() )

  @git_temp_home_func()
  def test_list_remote_tags(self):
    r1 = self._make_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('1.0.0')
    r1.push_tag('1.0.0')
    r1.tag('1.0.1')
    r1.push_tag('1.0.1')
    self.assertEqual( [ '1.0.0', '1.0.1' ], r2.list_remote_tags() )

  @git_temp_home_func()
  def test_bump_tag(self):
    r1 = self._make_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('1.0.0')
    r1.push_tag('1.0.0')
    self.assertEqual( '1.0.0', r1.greatest_local_tag() )
    r1.bump_tag('revision', reset_lower = True)

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( '1.0.1', r2.greatest_local_tag() )

  @git_temp_home_func()
  def test_bump_tag_empty(self):
    r1 = self._make_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    self.assertEqual( None, r1.greatest_local_tag() )
    r1.bump_tag('revision', reset_lower = True)

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( '1.0.0', r2.greatest_local_tag() )

  @git_temp_home_func()
  def test_bump_two_components(self):
    r1 = self._make_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('1.0')
    r1.push_tag('1.0')
    self.assertEqual( '1.0', r1.greatest_local_tag() )
    r1.bump_tag('minor', reset_lower = True)

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( '1.1', r2.greatest_local_tag() )
    
  @git_temp_home_func()
  def test_list_local_tags_by_version(self):
    r = self._make_repo(remote = False)
    r.add_file('readme.txt', 'readme is good')
    r.tag('1.0.0')
    r.tag('1.0.1')
    r.tag('1.0.4')
    r.tag('1.0.5')
    r.tag('1.0.9')
    r.tag('1.0.11')
    self.assertEqual( [ '1.0.9', '1.0.11' ], r.list_local_tags_gt('1.0.5') )
    self.assertEqual( [ '1.0.5', '1.0.9', '1.0.11' ], r.list_local_tags_ge('1.0.5') )
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.4' ], r.list_local_tags_lt('1.0.5') )
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.4', '1.0.5' ], r.list_local_tags_le('1.0.5') )
    
  @git_temp_home_func()
  def test_list_remote_tags_by_version(self):
    r1 = self._make_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    all_tags = [ '1.0.0', '1.0.1','1.0.4','1.0.5','1.0.9','1.0.11' ]
    for tag in all_tags:
      r1.tag(tag)
      r1.push_tag(tag)
    self.assertEqual( all_tags, r2.list_remote_tags() )
    self.assertEqual( [ '1.0.9', '1.0.11' ], r2.list_remote_tags_gt('1.0.5') )
    self.assertEqual( [ '1.0.5', '1.0.9', '1.0.11' ], r2.list_remote_tags_ge('1.0.5') )
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.4' ], r2.list_remote_tags_lt('1.0.5') )
    self.assertEqual( [ '1.0.0', '1.0.1', '1.0.4', '1.0.5' ], r2.list_remote_tags_le('1.0.5') )

  @git_temp_home_func()
  def test_save_file_first_time(self):
    r1 = self._make_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.save_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r2.pull()
    self.assertEqual( 'readme is good', r2.read_file('readme.txt') )
    
  @git_temp_home_func()
  def test_save_file_modify(self):
    r1 = self._make_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
#    r1.save_file('readme.txt', 'readme is bad')
#    r1.push('origin', 'master')
#    r2.pull()
#    self.assertEqual( 'readme is bad', r2.read_file('readme.txt') )
    
  @git_temp_home_func()
  def xtest_reset_to_revision(self):
    r1 = self._make_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r3 = r1.make_temp_cloned_repo()

    r2.pull()
    r3.pull()

    r2.save_file('readme.txt', 'readme 2')
    r2.push()
    
    r3.save_file('readme.txt', 'conflicted 1')
    with self.assertRaises(RuntimeError) as ctx:
      r3.push()
      
    r3.reset_to_revision('@{u}')
    r3.pull()
    r3.save_file('readme.txt', 'conflicted 1')
    r3.push()

  @git_temp_home_func()
  def test_list_branches_just_master(self):
    r1 = self._make_repo()
    commit = r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( [
      ( 'master', 'both', True, 0, 0, commit, 'unittest', 'add readme.txt' ),
    ], r2.list_branches('both') )

  @git_temp_home_func()
  def test_list_branches_create_inactive(self):
    r1 = self._make_repo()
    commit = r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r2.branch_create('b1', checkout = False)
    self.assertEqual( [
      ( 'b1', 'local', False, 0, 0, commit, 'unittest', 'add readme.txt' ),
      ( 'master', 'both', True, 0, 0, commit, 'unittest', 'add readme.txt' ),
    ], r2.list_branches('both') )
    
  @git_temp_home_func()
  def test_list_branches_create_active(self):
    r1 = self._make_repo()
    commit = r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r2.branch_create('b1', checkout = True)
    self.assertEqual( [
      ( 'b1', 'local', True, 0, 0, commit, 'unittest', 'add readme.txt' ),
      ( 'master', 'both', False, 0, 0, commit, 'unittest', 'add readme.txt' ),
    ], r2.list_branches('both') )
    
  @git_temp_home_func()
  def test_list_branches_create_push(self):
    r1 = self._make_repo()
    commit = r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r2.branch_create('b1', checkout = True, push = True)
    self.assertEqual( [
      ( 'b1', 'both', True, 0, 0, commit, 'unittest', 'add readme.txt' ),
      ( 'master', 'both', False, 0, 0, commit, 'unittest', 'add readme.txt' ),
    ], r2.list_branches('both') )
    
  @git_temp_home_func()
  def test_branch_status(self):
    r1 = self._make_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r3 = r1.make_temp_cloned_repo()
    self.assertEqual( ( 0, 0 ), r2.branch_status() )
    r2.add_file('foo.txt', 'foo.txt')
    self.assertEqual( ( 1, 0 ), r2.branch_status() )
    r2.add_file('bar.txt', 'bar.txt')

    self.assertEqual( ( 0, 0 ), r3.branch_status() )
    r2.push()
    r3.fetch()
    self.assertEqual( ( 0, 2 ), r3.branch_status() )

  @git_temp_home_func()
  def test_add_file_with_commit(self):
    r1 = self._make_repo(content = [ 'file readme.txt "readme is good" 644' ])
    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( [ 'readme.txt' ], r2.find_all_files() )

    commit1 = r1.last_commit_hash()
    r1.add_file('orange.txt', 'orange is good', commit = True)
    commit2 = r1.last_commit_hash()
    self.assertNotEqual( commit1, commit2 )
    r1.push()
    r2.pull()
    self.assertEqual( [ 'orange.txt', 'readme.txt' ], r2.find_all_files() )

  @git_temp_home_func()
  def test_add_file_with_no_commit(self):
    r1 = self._make_repo(content = [ 'file readme.txt "readme is good" 644' ])
    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( [ 'readme.txt' ], r2.find_all_files() )

    commit1 = r1.last_commit_hash()
    r1.add_file('orange.txt', 'orange is good', commit = False)
    commit2 = r1.last_commit_hash()
    self.assertEqual( commit1, commit2 )
    r1.push()
    r2.pull()
    self.assertEqual( [ 'readme.txt' ], r2.find_all_files() )
      
  @git_temp_home_func()
  def test_files_for_commit(self):
    r1 = self._make_repo(content = [ 'file readme.txt "readme is good" 644' ], prefix = 'r1-')
    r1.add_file('orange.txt', 'orange is good', commit = False)
    r1.add_file('kiwi.txt', 'kiwi is good', commit = False)
    r1.add([ 'orange.txt', 'kiwi.txt' ])
    r1.commit('add stuff', [ 'orange.txt', 'kiwi.txt' ])
    r1.push()
      
    r2 = r1.make_temp_cloned_repo(prefix = 'r2-')
    self.assertEqual( [ 'kiwi.txt', 'orange.txt' ], r2.files_for_commit(r2.last_commit_hash()) )

  @git_temp_home_func()
  def test_active_branch(self):
    r1 = self._make_repo(content = [ 'file readme.txt "readme is good" 644' ], prefix = 'r1-')
    r1.branch_create('b1', checkout = False, push = True)
      
    r2 = r1.make_temp_cloned_repo(prefix = 'r2-')
    self.assertEqual( 'master', r2.active_branch() )
    r2.checkout('b1')
    self.assertEqual( 'b1', r2.active_branch() )
    r2.checkout('master')
    self.assertEqual( 'master', r2.active_branch() )

  @git_temp_home_func()
  def test_remove(self):
    r = self._make_repo(remote = True)
    r.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r.add('.')
    r.commit('add', '.')
    r.remove('d/e/bar.txt')
    r.commit('remove', 'd/e/bar.txt')
    r.push()

  @git_temp_home_func()
  def test_has_unpushed_commits(self):
    r = self._make_repo(remote = True)
    r.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r.add([ 'foo.txt' ])
    r.commit('add foo.txt', [ 'foo.txt' ])
    r.push('origin', 'master')
    self.assertFalse( r.has_unpushed_commits() )
    r.add_file('bar.txt', 'this is bar.txt', commit = True)
    self.assertTrue( r.has_unpushed_commits() )

  @git_temp_home_func()
  def test_has_local_tag(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    r.tag('foo-1.0.0', push = False)
    self.assertTrue( r.has_local_tag('foo-1.0.0') )
    self.assertFalse( r.has_remote_tag('foo-1.0.0') )
    
  @git_temp_home_func()
  def test_has_remote_tag(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    r.tag('foo-1.0.0', push = False)
    self.assertTrue( r.has_local_tag('foo-1.0.0') )
    self.assertFalse( r.has_remote_tag('foo-1.0.0') )
    r.push_tag('foo-1.0.0')
    self.assertTrue( r.has_remote_tag('foo-1.0.0') )
    
  @git_temp_home_func()
  def test_has_commit_exists(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    commit1 = r.add_file('bar.txt', 'this is bar.txt')
    commit2 = r.add_file('baz.txt', 'this is baz.txt')
    self.assertTrue( r.has_commit(commit1) )
    self.assertTrue( r.has_commit(commit2) )
    
  @git_temp_home_func()
  def test_has_commit_does_not_exist(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    commit1 = r.add_file('bar.txt', 'this is bar.txt')
    commit2 = r.add_file('baz.txt', 'this is baz.txt')
    self.assertFalse( r.has_commit('0000000') )
    
  @git_temp_home_func()
  def test_has_commit_invalid_hash(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    commit1 = r.add_file('bar.txt', 'this is bar.txt')
    commit2 = r.add_file('baz.txt', 'this is baz.txt')
    self.assertFalse( r.has_commit('invalidhash') )
    
  @git_temp_home_func()
  def test_has_revision(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    commit1 = r.add_file('bar.txt', 'this is bar.txt')
    r.tag('foo-1.0.0', push = False)
    commit2 = r.add_file('baz.txt', 'this is baz.txt')
    r.tag('foo-1.0.1', push = False)
    self.assertFalse( r.has_revision('0000000') )
    self.assertTrue( r.has_revision(commit1) )
    self.assertTrue( r.has_revision(commit2) )
    self.assertTrue( r.has_revision('foo-1.0.0') )
    self.assertTrue( r.has_revision('foo-1.0.1') )
    self.assertFalse( r.has_revision('foo-1.0.2') )
    
  @git_temp_home_func()
  def test_submodule_set_branch(self):
    sub_content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    sub_repo = self._make_repo(remote = True, content = sub_content)
    
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)

    r.call_git('submodule add {} mod'.format(sub_repo.address))
    self.assertEqual( None, r.submodule_get_branch('mod') )
    r.submodule_set_branch('mod', 'foo')
    self.assertEqual( 'foo', r.submodule_get_branch('mod') )
    
  @git_temp_home_func()
  def test_submodule_init(self):
    sub_content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    sub_repo = self._make_repo(remote = True, content = sub_content, prefix = '-mod-')
    
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content, prefix = '-main-')
    self.assertEqual( [ 'foo.txt' ], r.find_all_files() )

    r.submodule_add(sub_repo.address, 'mod')
    r.commit('add mod submodule', '.')
    r.push()
    self.assertEqual( [ 'foo.txt', 'mod/subfoo.txt' ], r.find_all_files() )

    r2 = git_repo(self.make_temp_dir(), address = r.address)
    r2.clone()
    self.assertEqual( ( 'mod', None, sub_repo.last_commit_hash(), sub_repo.last_commit_hash(short_hash = True), False, None ),
                      r2.submodule_status_one('mod') )
    self.assertEqual( [ 'foo.txt' ], r2.find_all_files() )
    r2.submodule_init(submodule = 'mod')
    self.assertEqual( [ 'foo.txt', 'mod/subfoo.txt' ], r2.find_all_files() )
    self.assertEqual( ( 'mod', None, sub_repo.last_commit_hash(), sub_repo.last_commit_hash(short_hash = True), True, 'heads/master' ),
                      r2.submodule_status_one('mod') )
    
  @git_temp_home_func()
  def test_submodule_update_revision(self):
    sub_content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    sub_repo = self._make_repo(remote = True, content = sub_content, prefix = '-mod-')
    rev1 = sub_repo.last_commit_hash(short_hash = True)
    
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r1 = self._make_repo(remote = True, content = content, prefix = '-main-')
    self.assertEqual( [ 'foo.txt' ], r1.find_all_files() )

    r1.submodule_add(sub_repo.address, 'mod')
    r1.commit('add mod submodule', '.')
    r1.push()
    self.assertEqual( [ 'foo.txt', 'mod/subfoo.txt' ], r1.find_all_files() )

    rev2 = sub_repo.add_file('sub_kiwi.txt', 'this is sub_kiwi.txt', push = True)
    
    r2 = git_repo(self.make_temp_dir(), address = r1.address)
    r2.clone()
    r2.submodule_init(submodule = 'mod')
    self.assertEqual( rev1, r2.submodule_status_one('mod').revision )

    # check that setting the same revision returns false
    rv = r2.submodule_update_revision('mod', rev1)
    self.assertFalse( rv )
    
    rv = r2.submodule_update_revision('mod', rev2)
    self.assertTrue( rv )
    r2.commit('update mod', 'mod')
    r2.push()

    rv = r2.submodule_update_revision('mod', rev2)
    self.assertFalse( rv )
    
    r3 = git_repo(self.make_temp_dir(), address = r1.address)
    r3.clone()
    r3.submodule_init(submodule = 'mod')
    self.assertEqual( rev2, r3.submodule_status_one('mod').revision )

    rev3 = sub_repo.add_file('sub_orange.txt', 'this is sub_orange.txt', push = True)

    r4 = git_repo(self.make_temp_dir(), address = r1.address)
    r4.clone()
    r4.submodule_init(submodule = 'mod')
    self.assertEqual( rev2, r4.submodule_status_one('mod').revision )
    rv = r4.submodule_update_revision('mod', rev3)
    self.assertTrue( rv )
    r4.commit('update mod', 'mod')
    r4.push()
    self.assertEqual( rev3, r4.submodule_status_one('mod').revision )

    rev4 = sub_repo.add_file('sub_melon.txt', 'this is sub_melon.txt', push = True)
    
    r3.pull()
    r3.submodule_init(submodule = 'mod')
    self.assertEqual( rev3, r3.submodule_status_one('mod').revision )
    rv = r3.submodule_update_revision('mod', rev4)
    self.assertTrue( rv )
    r3.commit('update mod', 'mod')
    r3.push()
    self.assertEqual( rev4, r3.submodule_status_one('mod').revision )

  @git_temp_home_func()
  def test_is_long_hash(self):
    content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    r = self._make_repo(remote = True, content = content, prefix = '-mod-')
    self.assertTrue( r.is_long_hash(r.last_commit_hash(short_hash = False)) )
    self.assertFalse( r.is_long_hash(r.last_commit_hash(short_hash = True)) )


  @git_temp_home_func()
  def test_is_short_hash(self):
    content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    r = self._make_repo(remote = True, content = content, prefix = '-mod-')
    self.assertFalse( r.is_short_hash(r.last_commit_hash(short_hash = False)) )
    self.assertTrue( r.is_short_hash(r.last_commit_hash(short_hash = True)) )
    
  @git_temp_home_func()
  def test_short_hash(self):
    content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    r = self._make_repo(remote = True, content = content, prefix = '-mod-')
    long_hash = r.last_commit_hash(short_hash = False)
    short_hash = r.last_commit_hash(short_hash = True)
    self.assertEqual( short_hash, r.short_hash(long_hash) )
    self.assertEqual( short_hash, r.short_hash(short_hash) )

  @git_temp_home_func()
  def test_long_hash(self):
    content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    r = self._make_repo(remote = True, content = content, prefix = '-mod-')
    long_hash = r.last_commit_hash(short_hash = False)
    short_hash = r.last_commit_hash(short_hash = True)
    self.assertTrue( r.is_long_hash(long_hash) )
    self.assertFalse( r.is_long_hash(short_hash) )
    self.assertEqual( long_hash, r.long_hash(long_hash) )
    self.assertEqual( long_hash, r.long_hash(short_hash) )
    
  @git_temp_home_func()
  def test_revision_equals(self):
    content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    r = self._make_repo(remote = True, content = content, prefix = '-mod-')
    rev1_short = r.last_commit_hash(short_hash = True)
    rev1_long = r.last_commit_hash(short_hash = True)
    
    r.add_file('sub_kiwi.txt', 'this is sub_kiwi.txt', push = True)
    rev2_short = r.last_commit_hash(short_hash = True)
    rev2_long = r.last_commit_hash(short_hash = True)
    
    self.assertTrue( r.revision_equals(rev1_short, rev1_short) )
    self.assertTrue( r.revision_equals(rev1_long, rev1_short) )
    self.assertTrue( r.revision_equals(rev1_short, rev1_long) )
    self.assertTrue( r.revision_equals(rev1_long, rev1_long) )

  @git_temp_home_func()
  def test_operation_with_reset_basic(self):
    r1 = self._make_repo()
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    def _op(repo):
      repo.write_temp_content([
        'file bar.txt "this is bar" 644',
      ])
      repo.add('.')
    r2.operation_with_reset(_op, 'add bar.txt')
    self.assertEqual( 'this is foo', r2.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is bar', r2.read_file('bar.txt', codec = 'utf8') )

    r3 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo', r3.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is bar', r3.read_file('bar.txt', codec = 'utf8') )

  @git_temp_home_func()
  def test_operation_with_reset_basic_interface(self):
    r1 = self._make_repo()
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    class _op(git_operation_base):
      def run(op_self, repo):
        repo.write_temp_content([
          'file bar.txt "this is bar" 644',
         ])
        repo.add('.')
    r2.operation_with_reset(_op(), 'add bar.txt')
    self.assertEqual( 'this is foo', r2.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is bar', r2.read_file('bar.txt', codec = 'utf8') )

    r3 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo', r3.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is bar', r3.read_file('bar.txt', codec = 'utf8') )

  @git_temp_home_func()
  def test_operation_with_reset_seq_interface(self):
    r1 = self._make_repo()
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    class _op1(git_operation_base):
      def run(op_self, repo):
        repo.write_temp_content([
          'file kiwi.txt "this is kiwi" 644',
         ])
        repo.add('.')
    class _op2(git_operation_base):
      def run(op_self, repo):
        repo.write_temp_content([
          'file apple.txt "this is apple" 644',
         ])
        repo.add('.')
    ops = [ _op1(), _op2() ]
    r2.operation_with_reset(ops, 'add kiwi.txt')
    self.assertEqual( 'this is foo', r2.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is kiwi', r2.read_file('kiwi.txt', codec = 'utf8') )
    self.assertEqual( 'this is apple', r2.read_file('apple.txt', codec = 'utf8') )

    r3 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo', r3.read_file('foo.txt', codec = 'utf8') )
    self.assertEqual( 'this is kiwi', r3.read_file('kiwi.txt', codec = 'utf8') )
    self.assertEqual( 'this is apple', r3.read_file('apple.txt', codec = 'utf8') )
    
  @git_temp_home_func()
  def test_operation_with_reset_with_conflict(self):
    r1 = self._make_repo()
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r3 = r1.make_temp_cloned_repo()

    def _op2(repo):
      repo.write_temp_content([
        'file foo.txt "this is foo 2" 644',
      ])
    r2.operation_with_reset(_op2, 'hack foo.txt to 2')

    def _op3(repo):
      repo.write_temp_content([
        'file foo.txt "this is foo 3" 644',
      ])
    r3.operation_with_reset(_op3, 'hack foo.txt to 3')
    self.assertEqual( 'this is foo 3', r3.read_file('foo.txt', codec = 'utf8') )

    r4 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo 3', r4.read_file('foo.txt', codec = 'utf8') )

  @git_temp_home_func()
  def test_operation_with_reset_with_multiprocess_conflict(self):
    '''
    Create a bunch of processes trying to push to the same repo.
    This sometimes creates a git locking issue and tests the operation push retry code.
    '''
    r1 = self._make_repo()
    r1.write_temp_content([
      'file foo.txt "_foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    def worker(n):
      worker_tmp_root = self.make_temp_dir(suffix = 'worker-{}'.format(n))
      worker_repo = git_repo(worker_tmp_root, address = r1.address)
      worker_repo.clone_or_pull()
      worker_repo.checkout('master')
      
      def _op(repo):
        old_content = repo.read_file('foo.txt', codec = 'utf8')
        new_content = '{}\nworker {}'.format(old_content, n)
        fp = repo.file_path('foo.txt')
        file_util.save(fp, content = new_content, codec = 'utf8', mode = 0o644)
        
      worker_repo.operation_with_reset(_op, 'from worker {}'.format(n))

    num_jobs = 9
    
    jobs = []
    for i in range(num_jobs):
      p = multiprocessing.Process(target = worker, args = (i, ))
      jobs.append(p)
      p.start()

    for job in jobs:
      job.join()

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( [
      '_foo',
      'worker 0',
      'worker 1',
      'worker 2',
      'worker 3',
      'worker 4',
      'worker 5',
      'worker 6',
      'worker 7',
      'worker 8',
    ], sorted(r2.read_file('foo.txt', codec = 'utf8').split('\n')) )

  @git_temp_home_func()
  def test_atexit_reset(self):
    r = self._make_repo()
    r.write_temp_content([
      'file foo.txt "_foo" 644',
    ])
    r.add([ 'foo.txt' ])
    r.commit('add foo.txt', [ 'foo.txt' ])
    r.push('origin', 'master')

    tmp_script_content = '''\
from bes.git.git_repo import git_repo
r = git_repo("{}", address = "{}")
r.atexit_reset(revision = 'HEAD')
r.save_file('foo.txt', content = 'i hacked you', add = False, commit = False)
'''.format(r.root, r.address)
    
    tmp_script = self.make_temp_file(content = tmp_script_content, perm = 0o0755)

    cmd = [ sys.executable, tmp_script, r.root ]
    execute.execute(cmd)

    self.assertFalse( r.has_changes() )

  @git_temp_home_func()
  def test_has_local_branch(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    self.assertFalse( r.has_local_branch('kiwi') )
    r.branch_create('kiwi')
    self.assertTrue( r.has_local_branch('kiwi') )

  @git_temp_home_func()
  def test_has_remote_branch(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    self.assertFalse( r.has_remote_branch('kiwi') )
    r.branch_create('kiwi', push = True)
    self.assertTrue( r.has_local_branch('kiwi') )
    self.assertTrue( r.has_remote_branch('kiwi') )
    
  @git_temp_home_func()
  def test_reset(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r1 = self._make_repo(remote = True, content = content)
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    self.assertEqual( 'this is foo', r2.read_file('foo.txt') )
    r2.save_file('foo.txt', 'i hacked you', add = False, commit = False)
    self.assertEqual( 'i hacked you', r2.read_file('foo.txt') )
    r2.reset()
    self.assertEqual( 'this is foo', r2.read_file('foo.txt') )
    
  @git_temp_home_func()
  def test_clean(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    self.assertEqual( [ 'foo.txt' ], r.find_all_files() )
    r.save_file('garbage.txt', 'this is garbage', add = False, commit = False)
    self.assertEqual( [ 'foo.txt', 'garbage.txt' ], r.find_all_files() )
    r.clean()
    self.assertEqual( [ 'foo.txt' ], r.find_all_files() )

  @git_temp_home_func()
  def test_submodule_reset(self):
    sub_content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    sub_repo = self._make_repo(remote = True, content = sub_content, prefix = '-mod-')
    rev1 = sub_repo.last_commit_hash(short_hash = True)
    rev2 = sub_repo.add_file('sub_kiwi.txt', 'this is sub_kiwi.txt', push = True)
    
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r1 = self._make_repo(remote = True, content = content, prefix = '-main-')
    self.assertEqual( [ 'foo.txt' ], r1.find_all_files() )

    r1.submodule_add(sub_repo.address, 'mod')
    r1.commit('add mod submodule', '.')
    r1.push()
    self.assertEqual( [ 'foo.txt', 'mod/sub_kiwi.txt', 'mod/subfoo.txt' ], r1.find_all_files() )
    self.assertFalse( r1.has_changes(submodules = True) )

    rv = r1.submodule_update_revision('mod', rev1)
    self.assertTrue( rv )
    self.assertTrue( r1.has_changes(submodules = True) )
    r1.reset(submodules = True)
    self.assertFalse( r1.has_changes(submodules = True) )
    
  @git_temp_home_func()
  def test_submodule_clean(self):
    sub_content = [
      'file subfoo.txt "this is subfoo" 644',
    ]
    sub_repo = self._make_repo(remote = True, content = sub_content, prefix = '-mod-')
    rev1 = sub_repo.last_commit_hash(short_hash = True)
    rev2 = sub_repo.add_file('sub_kiwi.txt', 'this is sub_kiwi.txt', push = True)
    
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r1 = self._make_repo(remote = True, content = content, prefix = '-main-')
    self.assertEqual( [ 'foo.txt' ], r1.find_all_files() )

    r1.submodule_add(sub_repo.address, 'mod')
    r1.commit('add mod submodule', '.')
    r1.push()
    self.assertEqual( [ 'foo.txt', 'mod/sub_kiwi.txt', 'mod/subfoo.txt' ], r1.find_all_files() )
    self.assertFalse( r1.has_changes() )

    r1.save_file('mod/untracked_junk.txt', content = 'this is untracked junk', add = False, commit = False)
    self.assertTrue( r1.has_changes(untracked_files = True, submodules = True) )
    r1.clean(submodules = True)
    self.assertFalse( r1.has_changes(untracked_files = True, submodules = True) )
    
  @git_temp_home_func()
  def test_head_info_basic(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content, commit_message = 'message 1')
    c1 = r.last_commit_hash(short_hash = True)
    self.assertEqual( ( 'branch', 'master', None, c1, 'message 1', None ), r.head_info() )

  @git_temp_home_func()
  def test_head_info_empty_repo(self):
    'Test head_info() works on an empty just created repo.'
    tmp_dir = self.make_temp_dir()
    git.init(tmp_dir)
    r = git_repo(tmp_dir)
    self.assertEqual( ( 'nothing', None, None, None, None, None ), r.head_info() )
    
  @git_temp_home_func()
  def test_head_info_detached_head_at_commit(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content, commit_message = 'message 1')
    c1 = r.last_commit_hash(short_hash = True)
    r.add_file('bar.txt', 'this is bar')
    c2 = r.last_commit_hash(short_hash = True)
    r.checkout(c1)
    self.assertEqual( ( 'detached_commit', None, None, c1, 'message 1', [ 'master' ] ), r.head_info() )
    self.assertEqual( True, r.head_info().is_detached )
    self.assertEqual( False, r.head_info().is_tag )
    self.assertEqual( False, r.head_info().is_branch )
    self.assertEqual( 'detached_commit', r.head_info().state )
    self.assertEqual( 'detached_commit::{}'.format(c1), str(r.head_info()) )
    
  @git_temp_home_func()
  def test_head_info_detached_head_at_tag(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content, commit_message = 'message 1')
    c1 = r.last_commit_hash(short_hash = True)
    r.tag('1.2.3')
    r.add_file('bar.txt', 'this is bar')
    c2 = r.last_commit_hash(short_hash = True)
    r.checkout('1.2.3')
    self.assertEqual( ( 'tag', None, '1.2.3', c1, 'message 1', [ 'master' ] ), r.head_info() )
    self.assertEqual( True, r.head_info().is_tag )
    self.assertEqual( True, r.head_info().is_detached )
    self.assertEqual( False, r.head_info().is_branch )
    self.assertEqual( 'tag', r.head_info().state )
    self.assertEqual( 'tag:{}:{}'.format('1.2.3', c1), str(r.head_info()) )
    
  @git_temp_home_func()
  def test_head_info_detached_head_at_branch(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content, commit_message = 'message 1')
    c1 = r.last_commit_hash(short_hash = True)
    r.branch_create('b1', checkout = True)
    self.assertEqual( ( 'branch', 'b1', None, c1, 'message 1', None ), r.head_info() )
    self.assertEqual( False, r.head_info().is_detached )
    r.add_file('bar.txt', 'this is bar in b1', commit_message = 'message 2')
    c2 = r.last_commit_hash(short_hash = True)
    self.assertEqual( ( 'branch', 'b1', None, c2, 'message 2', None ), r.head_info() )
    self.assertEqual( False, r.head_info().is_tag )
    self.assertEqual( True, r.head_info().is_branch )
    self.assertEqual( 'branch', r.head_info().state )
    self.assertEqual( 'branch:{}:{}'.format('b1', c2), str(r.head_info()) )

  @git_temp_home_func()
  def test_head_info_detached_head_at_tag_in_branch(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content, commit_message = 'message 1')
    r.branch_create('b1', checkout = True)
    r.add_file('kiwi.txt', 'this is kiwi in b1', commit_message = 'message 2')
    c1 = r.last_commit_hash(short_hash = True)
    r.tag('1.2.3')
    r.checkout('master')
    r.branch_create('b2', checkout = True)
    r.add_file('lemon.txt', 'this is lemon in b1', commit_message = 'message 3')
    r.checkout('1.2.3')
    self.assertEqual( True, r.head_info().is_tag )
    self.assertEqual( False, r.head_info().is_branch )
    self.assertEqual( 'tag', r.head_info().state )
    self.assertEqual( 'tag:{}:{}'.format('1.2.3', c1), str(r.head_info()) )
    self.assertEqual( None, r.head_info().branch )
    self.assertEqual( [ 'b1' ], r.head_info().ref_branches )

  @git_temp_home_func()
  def test_head_info_detached_head_at_tag_in_branch_multiple_branches(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content, commit_message = 'message 1')
    r.branch_create('b1', checkout = True)
    r.add_file('kiwi.txt', 'this is kiwi in b1', commit_message = 'message 2')
    c1 = r.last_commit_hash(short_hash = True)
    r.tag('1.2.3')
    r.branch_create('b2', checkout = True)
    r.add_file('lemon.txt', 'this is lemon in b1', commit_message = 'message 3')
    r.checkout('1.2.3')
    self.assertEqual( True, r.head_info().is_tag )
    self.assertEqual( False, r.head_info().is_branch )
    self.assertEqual( 'tag', r.head_info().state )
    self.assertEqual( 'tag:{}:{}'.format('1.2.3', c1), str(r.head_info()) )
    self.assertEqual( None, r.head_info().branch )
    self.assertEqual( [ 'b1', 'b2' ], r.head_info().ref_branches )

  @git_temp_home_func()
  def test_head_info_detached_head_at_commit_in_branch(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content, commit_message = 'message 1')
    r.branch_create('b1', checkout = True)
    r.add_file('kiwi.txt', 'this is kiwi in b1', commit_message = 'message 2')
    c1 = r.last_commit_hash(short_hash = True)
    r.checkout('master')
    r.branch_create('b2', checkout = True)
    r.add_file('lemon.txt', 'this is lemon in b1', commit_message = 'message 3')
    r.checkout(c1)
    self.assertEqual( False, r.head_info().is_tag )
    self.assertEqual( False, r.head_info().is_branch )
    self.assertEqual( True, r.head_info().is_detached_commit )
    self.assertEqual( 'detached_commit', r.head_info().state )
    self.assertEqual( 'detached_commit::{}'.format(c1), str(r.head_info()) )
    self.assertEqual( None, r.head_info().branch )
    self.assertEqual( [ 'b1' ], r.head_info().ref_branches )

  @git_temp_home_func()
  def test_is_tag(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    commit1 = r.add_file('bar.txt', 'this is bar.txt')
    r.tag('foo-1.0.0', push = False)
    commit2 = r.add_file('baz.txt', 'this is baz.txt')
    r.tag('foo-1.0.1', push = False)
    self.assertTrue( r.is_tag('foo-1.0.0') )
    self.assertTrue( r.is_tag('foo-1.0.1') )
    self.assertFalse( r.is_tag('foo-1.0.2') )
    self.assertFalse( r.is_tag(commit1) )
    self.assertFalse( r.is_tag(commit2) )
    r.branch_create('b1', checkout = True)
    self.assertFalse( r.is_tag('b1') )

  @git_temp_home_func()
  def test_is_branch(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    c1 = r.add_file('bar.txt', 'this is bar.txt')
    r.tag('t1')
    r.branch_create('b1', checkout = True)
    c2 = r.add_file('baz.txt', 'this is baz.txt')
    r.tag('t2')
    r.checkout('master')
    r.branch_create('b2', checkout = True)
    self.assertFalse( r.is_branch('t1') )
    self.assertFalse( r.is_branch('t2') )
    self.assertTrue( r.is_branch('b1') )
    self.assertTrue( r.is_branch('b2') )
    self.assertFalse( r.is_branch('notthere') )

  @git_temp_home_func()
  def test_branches_for_tag_single_branch(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    r.branch_create('b1', checkout = True)
    c1 = r.add_file('kiwi.txt', 'this is kiwi.txt')
    r.tag('t1')
    r.checkout('master')
    r.branch_create('b2')
    c2 = r.add_file('apple.txt', 'this is apple.txt')
    r.checkout('master')
    r.branch_create('b3', checkout = True)
    self.assertEqual( [ 'b1' ], r.branches_for_tag('t1') )

  @git_temp_home_func()
  def test_branches_for_tag_multiple_branches(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    r.branch_create('b1', checkout = True)
    c1 = r.add_file('kiwi.txt', 'this is kiwi.txt')
    r.tag('t1')
    r.branch_create('b2')
    c2 = r.add_file('apple.txt', 'this is apple.txt')
    r.checkout('master')
    r.branch_create('b3')
    self.assertEqual( [ 'b1', 'b2' ] , r.branches_for_tag('t1') )

  @git_temp_home_func()
  def test_branches_for_tag_detached_head(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    r.branch_create('b1', checkout = True)
    c1 = r.add_file('kiwi.txt', 'this is kiwi.txt')
    r.tag('t1')
    r.checkout('master')
    r.branch_create('b2')
    c2 = r.add_file('apple.txt', 'this is apple.txt')
    r.checkout('master')
    r.branch_create('b3', checkout = True)
    r.checkout('t1')
    self.assertEqual( [ 'b1' ], r.branches_for_tag('t1') )

  @git_temp_home_func()
  def test_rsync_dir(self):
    src_content = [
      'file foo/bar/kiwi.txt "this is kiwi" 644',
    ]
    src_repo = self._make_repo(remote = True, content = src_content)

    dst_content = [
      'file apple.txt "this is apple" 644',
    ]
    dst_repo = self._make_repo(remote = True, content = dst_content)
    
#    r.branch_create('b1', checkout = True)
#    c1 = r.add_file('kiwi.txt', 'this is kiwi.txt')
#    r.tag('t1')
#    r.checkout('master')
#    r.branch_create('b2')
#    c2 = r.add_file('apple.txt', 'this is apple.txt')
#    r.checkout('master')
#    r.branch_create('b3', checkout = True)
#    r.checkout('t1')
#    self.assertEqual( [ 'b1' ], r.branches_for_tag('t1') )

  @git_temp_home_func()
  def test_tag_with_commit(self):
    content = [
      'file foo.txt "this is foo" 644',
    ]
    r = self._make_repo(remote = True, content = content)
    c1 = r.add_file('kiwi.txt', 'this is kiwi.txt')
    c2 = r.add_file('lemon.txt', 'this is lemon.txt')
    r.tag('t1')
    c3 = r.add_file('apple.txt', 'this is apple.txt')
    r.tag('t2')
    r.tag('t3', commit = c1)
    self.assertEqual( c3, r.ref_info('t3').commit_short )

  @git_temp_home_func()
  def test_operation_with_reset_wrong_function_args(self):
    r1 = self._make_repo()
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()

    def _op(repo, bad_arg):
      pass
    with self.assertRaises(git_error) as ctx:
      r2.operation_with_reset(_op, 'add bar.txt')
    
if __name__ == '__main__':
  unit_test.main()
