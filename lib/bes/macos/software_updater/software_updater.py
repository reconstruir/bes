#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.system.host import host
from bes.text.tree_text_parser import tree_text_parser
from bes.common.algorithm import algorithm

from .software_updater_item import software_updater_item

class software_updater(object):
  'Class to deal with the macos softwareupdate program.'

  @classmethod
  def _parse_list_output(clazz, text):
    'Parse the output of softwareupdate --list.'
    result = []
    root = tree_text_parser.parse(text)
    for child in root.children:
      text = child.data.text
      if text.startswith('* Label'):
        assert len(child.children) == 1
        label = clazz._parse_label(text)
        title, version, size, recommended = clazz._parse_attributes(child.children[0])
        item = software_updater_item(title, label, version, size, recommended == 'YES')
        result.append(item)
    return sorted(algorithm.unique(result))

  _LABEL_PATTERN = r'^\* Label:\s+(.+)\s*$'
  @classmethod
  def _parse_label(clazz, text):
    f = re.findall(clazz._LABEL_PATTERN, text)
    assert len(f) == 1
    return f[0]
                                     
  _ATTRIBUTES_PATTERN = r'^Title:\s+(.+),\s+Version:\s+(.+),\s+Size:\s+(.+),\s+Recommended:\s+(.+),\s*$'
  @classmethod
  def _parse_attributes(clazz, node):
    f = re.findall(clazz._ATTRIBUTES_PATTERN, node.data.text)
    assert len(f) == 1
    assert len(f[0]) == 4
    return f[0]
