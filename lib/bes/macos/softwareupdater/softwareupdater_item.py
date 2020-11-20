# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

class softwareupdater_item(namedtuple('softwareupdater_item', 'title, label, version, size, recommended')):
  'A class to deal with a single macos softwareupdater item.'
  
  def __new__(clazz, title, label, version, size, recommended):
    check.check_string(title)
    check.check_string(label)
    check.check_string(version)
    check.check_string(size)
    check.check_bool(recommended)

    return clazz.__bases__[0].__new__(clazz, title, label, version, size, recommended)
