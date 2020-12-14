#!/usr/bin/env python
# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path, getcwd, remove
from bes.git.git_temp_repo import git_temp_repo
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.git.git_unit_test import git_temp_home_func

from bes.testing.program_unit_test import program_unit_test

class test_git_repo_document_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '..', '..', '..', '..', 'bin', 'best.py')
  
  @git_temp_home_func()
  def test_basic(self):
    # This is the document to write to the repository.
    tmp_source_doc = self.make_temp_file(content = 'abc', suffix = '-doc.txt')

    # Here's a repository to put it in.
    r = git_temp_repo(debug=self.DEBUG)
    r.add_file('dummy.txt', content = 'dummy')
    r.push('origin', 'master')

    # Use this directory for the document DB's local repository. It will be deleted at the end of
    # the test.
    tmp_db_dir = self.make_temp_dir()

    # Run the 'egoist.py git update <source-doc> <repo-address> <branch>' command.
    args = [
      'git_repo_document',
      'update',
      tmp_source_doc,
      r.address,
      'master',
      '--working-dir',
      tmp_db_dir,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)

    # Also check doc is in repo. It will have the same name as the source doc.
    filename = path.basename(tmp_source_doc)
    r.pull()
    contents = r.read_file(filename)
    self.assertEqual(contents, 'abc')

    # Since we now have a file in the repo, let's also test whether load_document can read it.

    # Here's an auto-delete temp directory for the document DB's local repository.
    tmp_db_dir2 = temp_file.make_temp_dir(delete = not self.DEBUG)

    # By default, the CLI will put the output file in a file with the same name as the file in
    # the repo, in the current directory.
    tmp_target_filepath = path.join(getcwd(), filename)
    if path.exists(tmp_target_filepath):
      remove(tmp_target_filepath)

    # Run the CLI.
    args = [
      'git_repo_document',
      'load',
      filename,
      r.address,
      'master',
      '--working-dir',
      tmp_db_dir2,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)

    # See if the file and contents are there.
    actual = file_util.read(tmp_target_filepath)
    self.assertEqual(actual, b'abc')

    # This will cause an exception and fail the test if the file wasn't created by the CLI.
    remove(tmp_target_filepath)

if __name__ == '__main__':
  program_unit_test.main()
