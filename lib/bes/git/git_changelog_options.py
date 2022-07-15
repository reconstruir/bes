# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


from ..system.check import check


class git_changelog_options(object):

  def __init__(self, **kargs):
    self._check_options(kargs)

    self.max_chars = kargs.get('max_chars', None)
    self.revision_chars = kargs.get('revision_chars', 7)
    self.message_chars = kargs.get('message_chars', None)
    self.balance = kargs.get('balance', 0.5)
    self.disable_date = kargs.get('disable_date', False)
    self.disable_author = kargs.get('disable_author', False)
    self.drop_message = kargs.get('drop_message', '[dropped]')

  @staticmethod
  def _check_options(kargs):
    max_chars = kargs.get('max_chars', None)
    revision_chars = kargs.get('revision_chars', 7)
    message_chars = kargs.get('message_chars', None)
    balance = kargs.get('balance', 0.5)
    disable_date = kargs.get('disable_date', False)
    disable_author = kargs.get('disable_author', False)
    drop_message = kargs.get('drop_message', '[dropped]')

    check.check_int(max_chars, allow_none=True)
    check.check_int(revision_chars)
    check.check_int(message_chars, allow_none=True)
    check.check_float(balance)
    check.check_bool(disable_date)
    check.check_bool(disable_author)
    check.check_string(drop_message, allow_none=True)

    if max_chars and max_chars < 100:
      raise ValueError("max_chars argument can't be less than 100")
    if revision_chars < 1:
      raise ValueError("revision_chars argument can't be less than 1")
    if message_chars and message_chars < 1:
      raise ValueError("message_chars argument can't be less than 1")
    if balance <= 0 or balance > 1:
      raise ValueError("balance argument value must be inside next range - (0, 1]")

  def __str__(self):
    return str(self.__dict__)
