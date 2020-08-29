# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .git_error import git_error

class git_commit_hash(object):
  'A class to deal with git commit hashes.'

  _MAX_LENGTH = 40
  _MIN_LENGTH = 4
  _SHORT_HASH_LENGTH = 7
  _LONG_HASH_LENGTH = 40

  @classmethod
  def is_valid_char(clazz, c):
    'Return True if c is a valid git hash char.'
    return (c >= 'a' and c <= 'f') or (c >= '0' and c <= '9')

  @classmethod
  def is_valid(clazz, h):
    'Return True if h is a valid git hash.'
    if not check.is_string(h):
      return False
    l = len(h)
    if l < clazz._MIN_LENGTH:
      return False
    if l > clazz._MAX_LENGTH:
      return False
    for c in h:
      if not clazz.is_valid_char(c):
        return False
    return True

  @classmethod
  def is_long(clazz, h):
    'Return True if h is a valid git long hash.'
    return clazz.is_valid(h) and len(h) == clazz._LONG_HASH_LENGTH

  @classmethod
  def is_short(clazz, h):
    'Return True if h is a valid git short hash.'
    return clazz.is_valid(h) and len(h) == clazz._SHORT_HASH_LENGTH

  @classmethod
  def shorten(clazz, h):
    'Return a short hash for h.'
    clazz.check_is_valid(h)
    return h[0:clazz._SHORT_HASH_LENGTH]

  @classmethod
  def check_is_valid(clazz, h):
    'Check that h is a valid hash and if not raise an error.'
    if not clazz.is_valid(h):
      raise git_error('Invalid hash: "{}"'.format(str(h)))

  @classmethod
  def check_is_short(clazz, h):
    'Check that h is a valid hash and if not raise an error.'
    if not clazz.is_short(h):
      raise git_error('Invalid short hash: "{}"'.format(str(h)))
    
  @classmethod
  def check_is_long(clazz, h):
    'Check that h is a valid hash and if not raise an error.'
    if not clazz.is_long(h):
      raise git_error('Invalid long hash: "{}"'.format(str(h)))
