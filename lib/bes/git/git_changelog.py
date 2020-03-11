# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


import re
import copy

from bes.common.check import check

from .git_commit_info import git_commit_info
from .git_changelog_options import git_changelog_options


class git_changelog:

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
  def truncate_changelog(clazz, list_of_commit_info, options):
    check.check_list(list_of_commit_info, entry_type=git_commit_info)

    list_of_commit_info = copy.deepcopy(list_of_commit_info)
    # disable date and/or author if needed
    clazz._disable_date(options.disable_date, list_of_commit_info)
    clazz._disable_author(options.disable_author, list_of_commit_info)

    result = '\n'.join(str(elem) for elem in list_of_commit_info)
    total_chars = len(result)

    if options.max_chars is None or total_chars <= options.max_chars:
      return result

    drop_functions = (
      clazz._drop_revisions,
      clazz._drop_date,
      clazz._drop_author,
      clazz._drop_merge_commit_messages,
      clazz._drop_commit_messages_and_lines
    )

    for drop_function in drop_functions:
      is_finished, total_chars = drop_function(list_of_commit_info, total_chars, options)
      if is_finished:
        return '\n'.join(str(elem) for elem in list_of_commit_info)

  @classmethod
  def truncate_changelogs(clazz, dict_of_list_of_commit_info, options):
    check.check_dict(dict_of_list_of_commit_info)

    if options.max_chars is None:
      result = ''
      for label in dict_of_list_of_commit_info:
        result += '\n\n{}\n'.format(label)
        # disable date and/or author if needed
        clazz._disable_date(options.disable_date, dict_of_list_of_commit_info[label])
        clazz._disable_author(options.disable_author, dict_of_list_of_commit_info[label])

        result += '\n'.join(str(elem) for elem in dict_of_list_of_commit_info[label])

      return result.strip()

    keys = dict_of_list_of_commit_info.keys()
    addional_length = len(''.join(keys)) + 3 * len(keys) - 1
    max_chars_bit = (options.max_chars - addional_length) // len(keys)

    changelog_blocks = []
    for label in dict_of_list_of_commit_info:
      label_options = clazz._create_label_options(max_chars_bit, options)
      changelog = clazz.truncate_changelog(dict_of_list_of_commit_info[label], label_options)
      changelog_blocks.append('{}:\n{}'.format(label, changelog))

    return '\n\n'.join(changelog_blocks)

  @staticmethod
  def _drop_revisions(list_of_commit_info, total_chars, options):
    for commit_info in list_of_commit_info:
      start_length = len(commit_info.revision)
      commit_info.revision = commit_info.revision[:options.revision_chars]
      total_chars -= start_length - options.revision_chars

    is_finished = total_chars <= options.max_chars
    return is_finished, total_chars

  @staticmethod
  def _drop_date(list_of_commit_info, total_chars, options):
    if not options.disable_date:
      for commit_info in list_of_commit_info:
        start_length = len(commit_info.date)
        commit_info.date = None
        total_chars -= start_length + 1

    is_finished = total_chars <= options.max_chars
    return is_finished, total_chars

  @staticmethod
  def _drop_author(list_of_commit_info, total_chars, options):
    if not options.disable_author:
      for commit_info in list_of_commit_info:
        start_length = len(commit_info.author) if commit_info.author else len(commit_info.email)
        commit_info.author = None
        commit_info.email = None
        total_chars -= start_length + 1

    is_finished = total_chars <= options.max_chars
    return is_finished, total_chars

  @staticmethod
  def _drop_merge_commit_messages(list_of_commit_info, total_chars, options):
    list_of_commit_info = list_of_commit_info[::-1]

    for commit_info in list_of_commit_info:
      if commit_info.is_merge_commit:
        start_length = len(commit_info.message)
        commit_info.message = commit_info.message[:options.message_chars] if options.message_chars else options.drop_message
        total_chars -= start_length - len(commit_info.message)

        if total_chars <= options.max_chars:
          return True, total_chars

    return False, total_chars

  @staticmethod
  def _drop_commit_messages_and_lines(list_of_commit_info, total_chars, options):
    list_of_commit_info.reverse()

    while total_chars > options.max_chars:
      # the purpose of this line is sync total_chars parameter (BUG)
      total_chars = len('\n'.join(str(elem) for elem in list_of_commit_info))

      limit = int(len(list_of_commit_info) * options.balance) + 1
      for index, commit_info in enumerate(list_of_commit_info):
        if index == limit:
          break

        if commit_info.message != options.drop_message:
          start_length = len(commit_info.message)
          commit_info.message = commit_info.message[:options.message_chars] if options.message_chars else options.drop_message
          total_chars -= start_length - len(commit_info.message)

          if total_chars <= options.max_chars:
            list_of_commit_info.reverse()
            return True, total_chars

      index = 0
      length = len(list_of_commit_info)
      while index < length:
        if index == limit:
          break

        start_length = len(list_of_commit_info[index])
        total_chars -= start_length + 1

        if total_chars <= options.max_chars:
          list_of_commit_info[:index + 1] = []
          list_of_commit_info.reverse()
          return True, total_chars

        index += 1
      list_of_commit_info[:index + 1] = []

    raise Exception('algorith is invalid for this case')

  @staticmethod
  def _disable_date(disable_date, list_of_commit_info):
    if disable_date:
      for commit_info in list_of_commit_info:
        commit_info.date = None

  @staticmethod
  def _disable_author(disable_author, list_of_commit_info):
    if disable_author:
      for commit_info in list_of_commit_info:
        commit_info.author = None
        commit_info.email = None

  @staticmethod
  def _create_label_options(max_chars_bit, options):
    return git_changelog_options(
      max_chars=max_chars_bit,
      revision_chars=options.revision_chars,
      message_chars=options.message_chars,
      balance=options.balance,
      disable_date=options.disable_date,
      disable_author=options.disable_author,
    )
