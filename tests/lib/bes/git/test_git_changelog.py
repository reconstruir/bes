#!/usr/bin/env python
# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


from bes.fs.file_util import file_util
from bes.testing.unit_test import unit_test
from bes.git.git_changelog import git_changelog
from bes.git.git_changelog_options import git_changelog_options as options


def create_list_of_commit_info(filename):
  log = file_util.read(filename, codec='utf-8')
  log = log.strip()

  return git_changelog.convert_changelog_string(log)


class test_truncate_changelog(unit_test):
  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/git'

  def test_no_truncation(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))
    result_log = git_changelog.truncate_changelog(list_of_commit_info, options())
    original_log = file_util.read(self.data_path('result/log_no_truncation.txt'), codec='utf-8')
    original_log = original_log.strip()
    self.assertEqual(original_log, result_log)

  def test_disable_date(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))
    result_log = git_changelog.truncate_changelog(list_of_commit_info, options(disable_date=True))
    original_log = file_util.read(self.data_path('result/log_disable_date.txt'), codec='utf-8')
    original_log = original_log.strip()
    self.assertEqual(original_log, result_log)

  def test_disable_author(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))
    result_log = git_changelog.truncate_changelog(list_of_commit_info, options(disable_author=True))
    original_log = file_util.read(self.data_path('result/log_disable_author.txt'), codec='utf-8')
    original_log = original_log.strip()
    self.assertEqual(original_log, result_log)

  def test_disable_date_and_author(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))
    result_log = git_changelog.truncate_changelog(list_of_commit_info, options(disable_date=True, disable_author=True))
    original_log = file_util.read(self.data_path('result/log_disable_date_and_author.txt'), codec='utf-8')
    original_log = original_log.strip()
    self.assertEqual(original_log, result_log)

  def test_truncate_revisions_1(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(5668, 4148, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars, revision_chars=1))
      original_log = file_util.read(self.data_path('result/log_truncate_revisions_1.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_revisions_7(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(5668, 4381, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars, revision_chars=7))
      original_log = file_util.read(self.data_path('result/log_truncate_revisions_7.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_revisions_10(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(5668, 4498, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars, revision_chars=10))
      original_log = file_util.read(self.data_path('result/log_truncate_revisions_10.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)


if __name__ == '__main__':
  unit_test.main()
