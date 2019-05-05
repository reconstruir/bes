#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from bes.git import git
from bes.git.git_repo import git_repo
from bes.git.git_status import git_status
from bes.git.git_temp_repo import git_temp_repo
from bes.git.git_unit_test import git_unit_test

class test_git_repo(unit_test):

  @classmethod
  def setUpClass(clazz):
    git_unit_test.set_identity()

  @classmethod
  def tearDownClass(clazz):
    git_unit_test.unset_identity()
 
  def test_init(self):
    r = git_temp_repo(remote = False)
    self.assertEqual( [], r.status('.') )

  def test_exists_false(self):
    tmp_dir = temp_file.make_temp_dir()
    r = git_repo(tmp_dir)
    self.assertFalse( r.exists() )

  def test_exists_true(self):
    r = git_temp_repo(remote = False)
    self.assertTrue( r.exists() )

  def test_add(self):
    r = git_temp_repo(remote = False)
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
    
  def test_commit(self):
    r = git_temp_repo(remote = False)
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

  def test_pull(self):
    r1 = git_temp_repo(remote = False)
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

  def test_pull2(self):
    r1 = git_temp_repo(remote = False)
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
    self.assertEqual([ 'a/b/c/foo.txt', 'd/e/bar.txt'], r2.find_all_files() )

    r1.write_temp_content([
      'file kiwi.txt "kiwi" 644',
    ])
    r1.add('kiwi.txt')
    r1.commit('foo', 'kiwi.txt')
    r2.pull()
    self.assertEqual([ 'a/b/c/foo.txt', 'd/e/bar.txt', 'kiwi.txt' ], r2.find_all_files() )

  def test_clone_or_pull(self):
    r1 = git_temp_repo(remote = False)
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
    self.assertEqual([ 'a/b/c/foo.txt', 'd/e/bar.txt'], r2.find_all_files() )

    r1.write_temp_content([
      'file kiwi.txt "kiwi" 644',
    ])
    r1.add('kiwi.txt')
    r1.commit('foo', 'kiwi.txt')
    r2.pull()
    self.assertEqual([ 'a/b/c/foo.txt', 'd/e/bar.txt', 'kiwi.txt' ], r2.find_all_files() )
    
  def test_find_all_files(self):
    r = git_temp_repo(remote = False)
    self.assertEqual([], r.find_all_files() )
    r.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r.add('.')
    r.commit('foo', '.')
    self.assertEqual([ 'a/b/c/foo.txt', 'd/e/bar.txt'], r.find_all_files() )
   
  def test_push(self):
    r1 = git_temp_repo()
    r1.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r1.add([ 'foo.txt' ])
    r1.commit('add foo.txt', [ 'foo.txt' ])
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( 'this is foo', r2.read_file('foo.txt', codec = 'utf8') )
    
  def test_delete_remote_tags(self):
    r1 = git_temp_repo()
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

  def test_list_remote_tags(self):
    r1 = git_temp_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('1.0.0')
    r1.push_tag('1.0.0')
    r1.tag('1.0.1')
    r1.push_tag('1.0.1')
    self.assertEqual( [ '1.0.0', '1.0.1' ], r2.list_remote_tags() )

  def test_bump_tag(self):
    r1 = git_temp_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('1.0.0')
    r1.push_tag('1.0.0')
    self.assertEqual( '1.0.0', r1.greatest_local_tag() )
    r1.bump_tag()

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( '1.0.1', r2.greatest_local_tag() )

  def test_bump_tag_empty(self):
    r1 = git_temp_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    self.assertEqual( None, r1.greatest_local_tag() )
    r1.bump_tag()

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( '1.0.0', r2.greatest_local_tag() )

  def test_bump_two_components(self):
    r1 = git_temp_repo()
    r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r1.tag('1.0')
    r1.push_tag('1.0')
    self.assertEqual( '1.0', r1.greatest_local_tag() )
    r1.bump_tag()

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( '1.1', r2.greatest_local_tag() )
    
  def test_list_local_tags_by_version(self):
    r = git_temp_repo(remote = False)
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
    
  def test_list_remote_tags_by_version(self):
    r1 = git_temp_repo()
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

  def test_save_file_first_time(self):
    r1 = git_temp_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.save_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')
    r2.pull()
    self.assertEqual( 'readme is good', r2.read_file('readme.txt') )
    
  def test_save_file_modify(self):
    r1 = git_temp_repo()
    r2 = r1.make_temp_cloned_repo()
    r1.save_file('readme.txt', 'readme is good')
    r1.save_file('readme.txt', 'readme is bad')
    r1.push('origin', 'master')
    r2.pull()
    self.assertEqual( 'readme is bad', r2.read_file('readme.txt') )
    
  def test_reset_to_revision(self):
    r1 = git_temp_repo()
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

  def test_list_branches_just_master(self):
    r1 = git_temp_repo()
    commit = r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    self.assertEqual( [
      ( 'master', 'both', True, 0, 0, commit, 'add readme.txt' ),
    ], r2.list_branches('both') )

  def test_list_branches_create_inactive(self):
    r1 = git_temp_repo()
    commit = r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r2.branch_create('b1', checkout = False)
    self.assertEqual( [
      ( 'b1', 'local', False, 0, 0, commit, 'add readme.txt' ),
      ( 'master', 'both', True, 0, 0, commit, 'add readme.txt' ),
    ], r2.list_branches('both') )
    
  def test_list_branches_create_active(self):
    r1 = git_temp_repo()
    commit = r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r2.branch_create('b1', checkout = True)
    self.assertEqual( [
      ( 'b1', 'local', True, 0, 0, commit, 'add readme.txt' ),
      ( 'master', 'both', False, 0, 0, commit, 'add readme.txt' ),
    ], r2.list_branches('both') )
    
  def test_list_branches_create_push(self):
    r1 = git_temp_repo()
    commit = r1.add_file('readme.txt', 'readme is good')
    r1.push('origin', 'master')

    r2 = r1.make_temp_cloned_repo()
    r2.branch_create('b1', checkout = True, push = True)
    self.assertEqual( [
      ( 'b1', 'both', True, 0, 0, commit, 'add readme.txt' ),
      ( 'master', 'both', False, 0, 0, commit, 'add readme.txt' ),
    ], r2.list_branches('both') )
    
  def test_branch_status(self):
    r1 = git_temp_repo()
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
    
if __name__ == '__main__':
  unit_test.main()
