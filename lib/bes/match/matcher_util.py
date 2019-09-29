#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from .matcher_filename import matcher_multiple_filename
from .matcher_always_true import matcher_always_true
from .matcher_always_false import matcher_always_false

class matcher_util(object):
  'Some nice matching utilities.'

  @classmethod
  def match_filenames(clazz, filenames, include, exclude, ignore_case = False):
    if include:
      include_matcher = matcher_multiple_filename(include, ignore_case = ignore_case)
    else:
      include_matcher = matcher_always_true()
    if exclude:
      exclude_matcher = matcher_multiple_filename(exclude, ignore_case = ignore_case)
    else:
      exclude_matcher = matcher_always_false()
    result = []
    for f in filenames:
      should_include = include_matcher.match(f)
      should_exclude = exclude_matcher.match(f)
      if should_include and not should_exclude:
        result.append(f)
    return result
