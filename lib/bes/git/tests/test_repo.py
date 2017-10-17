#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import temp_file
from bes.git import git, repo, status

class test_repo(unit_test):

  def test_init(self):
    r = self._make_tmp_repo()
    self.assertEqual( [], r.status('.') )

  def test_exists_false(self):
    tmp_dir = temp_file.make_temp_dir()
    r = repo(tmp_dir)
    self.assertFalse( r.exists() )

  def test_exists_true(self):
    r = self._make_tmp_repo()
    self.assertTrue( r.exists() )

  def test_add(self):
    r = self._make_tmp_repo()
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
    r = self._make_tmp_repo()
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
    r1 = self._make_tmp_repo()
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

  def test_clone_or_pull(self):
    r1 = self._make_tmp_repo()
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
    
    
    '''
    r1.write_temp_content([ 'file new/stuff.txt "some stuff" 644' ])
    r1.add('new/stuff.txt')
    r1.commit('foo', 'new/stuff.txt')

    new_stuff_path = path.join(r2.root, 'new/stuff.txt')
    self.assertFalse( path.exists(new_stuff_path) )
    r2.pull()
    self.assertTrue( path.exists(new_stuff_path) )
'''    
  @classmethod
  def _make_tmp_repo(clazz, address = None):
    tmp_dir = temp_file.make_temp_dir()
    r = repo(tmp_dir, address = address)
    r.init()
    return r

  def test_find_all_files(self):
    r = self._make_tmp_repo()
    self.assertEqual([], r.find_all_files() )
    r.write_temp_content([
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ])
    r.add('.')
    r.commit('foo', '.')
    self.assertEqual([ 'a/b/c/foo.txt', 'd/e/bar.txt'], r.find_all_files() )
    
if __name__ == '__main__':
  unit_test.main()
