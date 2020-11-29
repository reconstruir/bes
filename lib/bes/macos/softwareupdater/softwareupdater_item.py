# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.check import check

class softwareupdater_item(namedtuple('softwareupdater_item', 'label, title, attributes')):
  'A class to deal with a single macos softwareupdater item.'
  
  def __new__(clazz, label, title, attributes):
    check.check_string(label)
    check.check_string(title)
    check.check_dict(attributes, check.STRING_TYPES)

    return clazz.__bases__[0].__new__(clazz, label, title, attributes)

  @property
  def version(self):
    return self.attributes.get('version', None)
  
  @property
  def size(self):
    return self.attributes.get('size', None)
  
