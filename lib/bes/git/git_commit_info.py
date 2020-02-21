# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


from bes.common.check import check


class git_commit_info(object):

  def __init__(self, revision, message, author=None, email=None, date=None):
    check.check_string(revision, allow_none=True)
    check.check_string(message, allow_none=True)
    check.check_string(author, allow_none=True)
    check.check_string(email, allow_none=True)
    check.check_string(date, allow_none=True)

    self.revision = revision
    self.message = message
    self.author = author
    self.email = email
    self.date = date

  def __str__(self):
    if self.revision and self.message:
      if self.author or self.email or self.date:
        text = 'commit {}\n'.format(self.revision)
        if self.author or self.email:
          text += 'Author: {} <{}>\n'.format(self.author, self.email)
        if self.date:
          text += 'Date: {}\n'.format(self.date)
        text += '\n    {}\n'.format(self.message)
        return text
      return '{} {}'.format(self.revision, self.message)
    return ''

  def __len__(self):
    return len(self.__str__())

  def is_merge_commit(self):
    return self.message.startswith('Merge branch')
