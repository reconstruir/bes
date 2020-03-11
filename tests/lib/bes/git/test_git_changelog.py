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

  def test_truncate_date(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(4381, 3182, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars))
      original_log = file_util.read(self.data_path('result/log_truncate_date.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_author(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(3182, 2770, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars))
      original_log = file_util.read(self.data_path('result/log_truncate_author.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_one_merge_commit(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(2770, 2730, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars))
      original_log = file_util.read(self.data_path('result/log_truncate_one_merge_commit.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_all_merge_commits(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(2310, 2270, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars))
      original_log = file_util.read(self.data_path('result/log_truncate_all_merge_commits.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_one_message(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(2270, 2260, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars))
      original_log = file_util.read(self.data_path('result/log_truncate_one_message.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_five_messages(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(2125, 2056, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars))
      original_log = file_util.read(self.data_path('result/log_truncate_five_messages.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_one_line(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(1510, 1492, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars))
      original_log = file_util.read(self.data_path('result/log_truncate_one_line.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_five_lines(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(1420, 1402, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars))
      original_log = file_util.read(self.data_path('result/log_truncate_five_lines.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_with_new_drop_message(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(1420, 1402, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars, drop_message='XxXxYyYyW'))
      original_log = file_util.read(self.data_path('result/log_truncate_with_new_drop_message.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_message_chars_9(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    for max_chars in range(1420, 1402, -1):
      result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=max_chars, message_chars=9))
      original_log = file_util.read(self.data_path('result/log_truncate_message_chars_9.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result_log)

  def test_truncate_max_chars_200(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('original/log.txt'))

    result_log = git_changelog.truncate_changelog(list_of_commit_info, options(max_chars=100))
    original_log = file_util.read(self.data_path('result/log_truncate_max_chars_100.txt'), codec='utf-8')
    original_log = original_log.strip()
    self.assertEqual(original_log, result_log)

  def test_invalid_type_for_list_of_commit_info(self):
    invalid_types = (None, True, 14, 15.6, 'a', ('a', 'b'), {'a': 'b'}, {'a'})

    for list_of_commit_info in invalid_types:
      with self.assertRaises(TypeError):
        git_changelog.truncate_changelog(list_of_commit_info, options())

  def test_invalid_inner_type_for_list_of_commit_info(self):
    invalid_inner_types = (None, True, 14, 15.6, 'a', ('a', 'b'), {'a': 'b'}, {'a'})

    for inner_type in invalid_inner_types:
      with self.assertRaises(TypeError):
        git_changelog.truncate_changelog([inner_type], options())


if __name__ == '__main__':
  unit_test.main()
