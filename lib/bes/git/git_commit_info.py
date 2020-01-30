# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


from bes.common.check import check


class git_commit_info(object):

  def __init__(self, revision, message):
    check.check_string(revision)
    check.check_string(message)

    self.revision = revision
    self.message = message

  def __str__(self):
    if self.revision and self.message:
      return '{} {}'.format(self.revision, self.message)
    return ''

  def __len__(self):
    return len(self.__str__())

  def is_merge_commit(self):
    return self.message.startswith('Merge branch')
