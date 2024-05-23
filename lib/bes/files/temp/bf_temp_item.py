#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.check import check

import os.path as path

from ..bf_file_ops import bf_file_ops

class bf_temp_item(namedtuple('bf_temp_item', 'filename, content, perm')):
  'Description of an temp item.'

  def __new__(clazz, filename, content = None, perm = None):
    return clazz.__bases__[0].__new__(clazz, filename, content, perm)

  def write(self, root_dir):
    check.check_string(root_dir)
    
    filename = path.join(root_dir, self.filename)
    if path.isfile(self.content):
      content = bf_file_ops.read(self.content)
    else:
      content = self.content
    bf_file_ops.save(filename, content = content, perm = self.perm)

check.register_class(bf_temp_item, include_seq = False)
    
