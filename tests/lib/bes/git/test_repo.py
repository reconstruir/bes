#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from bes.git import git, repo, status, temp_git_repo
from bes.git.git_unit_test import git_unit_test

class test_repo(unit_test):

  @classmethod
  def setUpClass(clazz):
    git_unit_test.set_identity()

  @classmethod
  def tearDownClass(clazz):
    git_unit_test.unset_identity()
 
  def test_init(self):
    r = temp_git_repo.make_temp_repo()
    self.assertEqual( [], r.status('.') )

  def test_exists_false(self):
    tmp_dir = temp_file.make_temp_dir()
    r = repo(tmp_dir)
    self.assertFalse( r.exists() )

  def test_exists_true(self):
    r = temp_git_repo.make_temp_repo()
    self.assertTrue( r.exists() )

  def test_add(self):
    r = temp_git_repo.make_temp_repo()
    r.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r.add('.')
    self.assertEqual( [
      status(status.ADDED, 'a/b/c/foo.txt'),
      status(status.ADDED, 'd/e/bar.txt'),
    ], r.status('.') )
    
  def test_commit(self):
    r = temp_git_repo.make_temp_repo()
    r.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r.add('.')
    self.assertEqual( [
      status(status.ADDED, 'a/b/c/foo.txt'),
      status(status.ADDED, 'd/e/bar.txt'),
    ], r.status('.') )
    r.commit('foo', '.')
    self.assertEqual( [], r.status('.') )

  def test_pull(self):
    r1 = temp_git_repo.make_temp_repo()
    r1.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r1.add('.')
    r1.commit('foo', '.')

    tmp_dir = temp_file.make_temp_dir()
    git.clone(r1.root, tmp_dir)
    r2 = repo(tmp_dir)
    self.assertEqual( [], r2.status('.') )

    r1.write_temp_content([ 'file new/stuff.txt "some stuff" 644' ])
    r1.add('new/stuff.txt')
    r1.commit('foo', 'new/stuff.txt')

    new_stuff_path = path.join(r2.root, 'new/stuff.txt')
    self.assertFalse( path.exists(new_stuff_path) )
    r2.pull()
    self.assertTrue( path.exists(new_stuff_path) )

  def test_pull2(self):
    r1 = temp_git_repo.make_temp_repo()
    r1.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r1.add('.')
    r1.commit('foo', '.')

    tmp_dir = temp_file.make_temp_dir()
    r2 = repo(tmp_dir, address = r1.root)
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
    r1 = temp_git_repo.make_temp_repo()
    r1.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r1.add('.')
    r1.commit('foo', '.')

    tmp_dir = temp_file.make_temp_dir()
    r2 = repo(tmp_dir, address = r1.root)
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
    r = temp_git_repo.make_temp_repo()
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
    r1 = temp_git_repo.make_temp_repo(init_args = [ '--bare', '--shared' ])
    
    r2 = temp_git_repo.make_temp_cloned_repo(r1.root)
    r2.write_temp_content([
      'file foo.txt "this is foo" 644',
    ])
    r2.add([ 'foo.txt' ])
    r2.commit('add foo.txt', [ 'foo.txt' ])
    r2.push('origin', 'master')

    r3 = temp_git_repo.make_temp_cloned_repo(r1.root)
    self.assertEqual( 'this is foo', file_util.read(path.join(r3.root, 'foo.txt'), codec = 'utf8') )
    
  def _make_temp_dir(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      pritn('tmp_dir: %s' % (tmp_dir))
    return tmp_dir
    
if __name__ == '__main__':
  unit_test.main()
