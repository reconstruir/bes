#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from .filename_util import filename_util

class filename_list(object):
  'Class to deal with file lists'

  @classmethod
  def prefixes(clazz, filenames, ignore_case = False):
    'Return a set of all the prefixes in filenames.'
    check.check_string_seq(filenames)

    prefixes = set()
    for filename in filenames:
      prefix = filename_util.prefix(filename)
      if ignore_case:
        prefix = prefix.lower()
      if prefix and prefix not in prefixes:
        prefixes.add(prefix)
    return prefixes
