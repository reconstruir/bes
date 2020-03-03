# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


import re
import copy

from bes.common.check import check

from .git_commit_info import git_commit_info


class git_changelog:

  @staticmethod
  def _check_algorithm_params(max_chars, revision_chars, balance):
    check.check_int(max_chars)
    check.check_int(revision_chars)
    check.check_float(balance)

    if max_chars < 1:
      raise ValueError("max_chars argument can't be less than 1")
    if revision_chars < 1:
      raise ValueError("revision_chars argument can't be less than 1")
    if balance <= 0 or balance > 1:
      raise ValueError("balance argument value must be inside next range - (0, 1]")

  @classmethod
  def convert_changelog_string(clazz, changelog_string):
    check.check_string(changelog_string)

    result = []

    commits = [elem.strip() for elem in changelog_string.split('\ncommit ') if elem]

    for commit in commits:
      commit_parts = [elem.strip() for elem in commit.split('\n') if elem]
      revision = commit_parts[0].split('commit ')[-1]
      revision = re.search(r'(\w+)\s*.*', revision).group(1)

      index = 1
      is_merge_commit = False
      if commit_parts[1].startswith('Merge: '):
        index += 1
        is_merge_commit = True
      email = re.search(r'Author: .*\s+<(.+)>', commit_parts[index]).group(1)
      author = email.split('@')[0]
      date = re.search(r'Date:\s+(.+)', commit_parts[index + 1]).group(1)
      message = ' '.join(commit_parts[index + 2:])

      result.append(git_commit_info(revision, message, author, email, date, is_merge_commit))

    return result

  @classmethod
  def truncate_changelog(clazz, list_of_commit_info, max_chars=4000, revision_chars=7, balance=0.5):
    check.check_list(list_of_commit_info, entry_type=git_commit_info)
    clazz._check_algorithm_params(max_chars, revision_chars, balance)

    list_of_commit_info = copy.deepcopy(list_of_commit_info)
    result = '\n'.join(str(elem) for elem in list_of_commit_info)
    total_chars = len(result)

    if total_chars <= max_chars:
      return result

    drop_functions_and_additional_arg = (
      (clazz._drop_revisions, revision_chars),
      (clazz._drop_merge_commit_messages, None),
      (clazz._drop_commit_messages_and_lines, balance)
    )

    for drop_function, additional_arg in drop_functions_and_additional_arg:
      args = [list_of_commit_info, total_chars, max_chars]
      if additional_arg:
        args.append(additional_arg)

      is_finished, total_chars = drop_function(*args)
      if is_finished:
        return '\n'.join(str(elem) for elem in list_of_commit_info)

  @classmethod
  def truncate_changelogs(clazz, dict_of_list_of_commit_info, max_chars=4000, revision_chars=7, balance=0.5):
    check.check_dict(dict_of_list_of_commit_info)
    clazz._check_algorithm_params(max_chars, revision_chars, balance)

    keys = dict_of_list_of_commit_info.keys()
    addional_length = len(''.join(keys)) + 3 * len(keys) - 1
    max_chars_bit = (max_chars - addional_length) // len(keys)

    changelog_blocks = []
    for label in dict_of_list_of_commit_info:
      changelog = clazz.truncate_changelog(dict_of_list_of_commit_info[label], max_chars_bit, revision_chars, balance)
      changelog_blocks.append('{}:\n{}'.format(label, changelog))

    return '\n\n'.join(changelog_blocks)

  @staticmethod
  def _drop_revisions(list_of_commit_info, total_chars, max_chars, limit):
    for commit_info in list_of_commit_info:
      start_length = len(commit_info.revision)
      commit_info.revision = commit_info.revision[:limit]
      total_chars -= start_length - limit

    is_finished = total_chars <= max_chars
    return is_finished, total_chars

  @staticmethod
  def _drop_merge_commit_messages(list_of_commit_info, total_chars, max_chars):
    list_of_commit_info = list_of_commit_info[::-1]

    for commit_info in list_of_commit_info:
      if commit_info.is_merge_commit:
        start_length = len(commit_info.message)
        commit_info.message = '[dropped]'
        total_chars -= start_length - len(commit_info.message)

        if total_chars <= max_chars:
          return True, total_chars

    return False, total_chars

  @staticmethod
  def _drop_commit_messages_and_lines(list_of_commit_info, total_chars, max_chars, balance):
    list_of_commit_info.reverse()

    while total_chars > max_chars:
      limit = int(len(list_of_commit_info) * balance) + 1
      for index, commit_info in enumerate(list_of_commit_info):
        if index == limit:
          break

        if commit_info.message != '[dropped]':
          start_length = len(commit_info.message)
          commit_info.message = '[dropped]'
          total_chars -= start_length - len(commit_info.message)

          if total_chars <= max_chars:
            list_of_commit_info.reverse()
            return True, total_chars

      index = 0
      length = len(list_of_commit_info)
      while index < length:
        if index == limit:
          break

        start_length = len(list_of_commit_info[0])
        total_chars -= start_length + 1

        if total_chars <= max_chars:
          list_of_commit_info[:index + 1] = []
          list_of_commit_info.reverse()
          return True, total_chars

        index += 1
      list_of_commit_info[:index + 1] = []

    raise Exception('algorith is invalid for this case')