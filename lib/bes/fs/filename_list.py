#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.char_util import char_util

class filename_list(object):
  'Class to deal with file lists'

  @classmethod
  def prefixes(clazz, filenames, ignore_case = False):
    'Return a set of all the prefixes in filenames.'
    check.check_string_seq(filenames)

    prefixes = set()
    for filename in filenames:
      prefix = clazz._prefix(filename)
      if ignore_case:
        prefix = prefix.lower()
      if prefix and prefix not in prefixes:
        prefixes.add(prefix)
    return prefixes

  @classmethod
  def _prefix(clazz, filename):
    'Return the extension for filename.'

    for i, c in enumerate(filename):
      if c.isdigit():
        return clazz._rstrip_punctiation(filename[0:i])
    return None

  @classmethod
  def _rstrip_punctiation(clazz, filename):
    for count, c in enumerate(reversed(filename)):
      if not char_util.is_punctuation(c):
        break
    if count == 0:
      return filename
    return filename[0 : -count]
