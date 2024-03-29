#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.git.git_temp_repo import git_temp_repo
from bes.archive.archiver import archiver
from bes.git.git_unit_test import git_temp_home_func

from bes.testing.program_unit_test import program_unit_test

class test_archive_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')

  @git_temp_home_func()
  def test_create_git_zip(self):
    content = [ 
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ]
    r = git_temp_repo(content = content, prefix = 'test_archive_', debug = self.DEBUG)
    commit = r.last_commit_hash(short_hash = True)
    
    tmp_archive = self.make_temp_file(suffix = '.zip')

    prefix = 'foo-{}'.format(commit)
    
    args = [
      'archive',
      'create_git',
      '--root-dir', r.root,
      '--format', 'zip',
      prefix,
      commit,
      tmp_archive,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'zip', archiver.format_name(tmp_archive) )
    expected = [
      '{}/a/b/c/foo.txt'.format(prefix),
      '{}/d/e/bar.txt'.format(prefix),
    ]
    actual = archiver.members(tmp_archive)
    self.assert_filename_list_equal( expected, actual )
    
  @git_temp_home_func()
  def test_create_git_tgz(self):
    content = [ 
      'file a/b/c/foo.txt "foo content" 755',
      'file d/e/bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ]
    r = git_temp_repo(content = content, prefix = 'test_archive_', debug = self.DEBUG)
    commit = r.last_commit_hash(short_hash = True)
    
    tmp_archive = self.make_temp_file(suffix = '.tgz')

    prefix = 'foo-{}'.format(commit)
    
    args = [
      'archive',
      'create_git',
      '--root-dir', r.root,
      '--format', 'tgz',
      prefix,
      commit,
      tmp_archive,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'tgz', archiver.format_name(tmp_archive) )
    expected = [
      '{}/a/b/c/foo.txt'.format(prefix),
      '{}/d/e/bar.txt'.format(prefix),
    ]
    actual = archiver.members(tmp_archive)
    self.assert_filename_list_equal( expected, actual )
    
if __name__ == '__main__':
  program_unit_test.main()
