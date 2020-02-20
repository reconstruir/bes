#!/usr/bin/env python
# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


from bes.fs.file_util import file_util
from bes.testing.unit_test import unit_test
from bes.git.git_changelog import git_changelog
from bes.git.git_commit_info import git_commit_info


def create_list_of_commit_info(filename):
  result = []
  log = file_util.read(filename, codec='utf-8')
  log = log.strip()

  for line in log.split('\n'):
    revision, message = line.split(' ', 1)
    commit_info = git_commit_info(revision, message)
    result.append(commit_info)

  return result


class test_truncate_changelog(unit_test):
  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/git'

  def test_no_truncation(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))
    result = git_changelog.truncate_changelog(list_of_commit_info)
    original_log = file_util.read(self.data_path('log.txt'), codec='utf-8')
    original_log = original_log.strip()
    self.assertEqual(original_log, result)

  def test_truncate_revisions_1(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(1200, 928, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars, revision_chars=1)
      original_log = file_util.read(self.data_path('log_revision_chars_1.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_truncate_revisions_7(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(1200, 1048, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)
      original_log = file_util.read(self.data_path('log_revision_chars_7.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_truncate_revisions_10(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(1200, 1109, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars, revision_chars=10)
      original_log = file_util.read(self.data_path('log_revision_chars_10.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_truncate_one_merge_commit_message(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(1048, 1008, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)
      original_log = file_util.read(self.data_path('log_one_merge_commit.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_truncate_two_merge_commit_messages(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(1008, 968, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)
      original_log = file_util.read(self.data_path('log_all_merge_commits.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_truncate_one_commit_message(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(968, 896, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)
      original_log = file_util.read(self.data_path('log_one_message.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_truncate_two_commit_messages(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(896, 878, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)
      original_log = file_util.read(self.data_path('log_two_messages.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_truncate_eleven_commit_messages(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(650, 636, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)
      original_log = file_util.read(self.data_path('log_eleven_messages.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_truncate_lines(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(510, 492, -1):
      result = git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)
      original_log = file_util.read(self.data_path('log_eight_lines.txt'), codec='utf-8')
      original_log = original_log.strip()
      self.assertEqual(original_log, result)

  def test_invalid_type_for_list_of_commit_info(self):
    invalid_types = (None, True, 14, 15.6, 'a', ('a', 'b'), {'a': 'b'}, {'a'})

    for list_of_commit_info in invalid_types:
      with self.assertRaises(TypeError):
        git_changelog.truncate_changelog(list_of_commit_info)

  def test_invalid_inner_type_for_list_of_commit_info(self):
    invalid_inner_types = (None, True, 14, 15.6, 'a', ('a', 'b'), {'a': 'b'}, {'a'})

    for inner_type in invalid_inner_types:
      with self.assertRaises(TypeError):
        git_changelog.truncate_changelog([inner_type])

  def test_invalid_type_for_max_chars(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))
    invalid_types = (None, 15.6, 'a', ('a', 'b'), {'a': 'b'}, {'a'})

    for max_chars in invalid_types:
      with self.assertRaises(TypeError):
        git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)

  def test_forbbiden_values_for_max_chars(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for max_chars in range(0, -10, -1):
      with self.assertRaises(ValueError):
        git_changelog.truncate_changelog(list_of_commit_info, max_chars=max_chars)

  def test_invalid_type_for_revision_chars(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))
    invalid_types = (None, 15.6, 'a', ('a', 'b'), {'a': 'b'}, {'a'})

    for revision_chars in invalid_types:
      with self.assertRaises(TypeError):
        git_changelog.truncate_changelog(list_of_commit_info, revision_chars=revision_chars)

  def test_forbbiden_values_for_revision_chars(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for revision_chars in range(0, -10, -1):
      with self.assertRaises(ValueError):
        git_changelog.truncate_changelog(list_of_commit_info, revision_chars=revision_chars)

  def test_invalid_type_for_balance(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))
    invalid_types = (None, 14, 'a', ('a', 'b'), {'a': 'b'}, {'a'})

    for balance in invalid_types:
      with self.assertRaises(TypeError):
        git_changelog.truncate_changelog(list_of_commit_info, balance=balance)

  def test_forbbiden_values_for_balance(self):
    list_of_commit_info = create_list_of_commit_info(self.data_path('log.txt'))

    for balance in (-10.0, -5.0, -1.0, -0.5, -0.001, -0.0, 1.001, 1.5, 2.0, 5.0, 10.0):
      with self.assertRaises(ValueError):
        git_changelog.truncate_changelog(list_of_commit_info, balance=balance)


class test_truncate_changelogs(unit_test):
  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/git'

  def test_truncate_three_repos(self):
    bes_commit_info = create_list_of_commit_info(self.data_path('log.txt'))
    rebuild_commit_info = create_list_of_commit_info(self.data_path('log_rebuild.txt'))
    ego_automation_commit_info = create_list_of_commit_info(self.data_path('log_ego_automation.txt'))

    dict_commit_info = {
      'bes': bes_commit_info,
      'rebuild': rebuild_commit_info,
      'ego_automation': ego_automation_commit_info
    }

    result = git_changelog.truncate_changelogs(dict_commit_info, max_chars=1400)
    original_log = file_util.read(self.data_path('log_three_repos.txt'), codec='utf-8')
    original_log = original_log.strip()
    self.assertEqual(original_log, result)

  def test_invalid_type_for_dict_of_list_of_commit_info(self):
    invalid_types = (None, True, 14, 15.6, 'a', ('a', 'b'), ['a', 'b'], {'a'})

    for dict_of_list_of_commit_info in invalid_types:
      with self.assertRaises(TypeError):
        git_changelog.truncate_changelogs(dict_of_list_of_commit_info)


if __name__ == '__main__':
  unit_test.main()
