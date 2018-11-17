#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, pkgutil
from bes.fs import file_util

class shell_framework(object):

  _FILES = [
    'env/bes_framework.sh',
  ]
  
  def __init__(self):
    pass
  
  def extract(self, where):
    for filename in self._FILES:
      content = pkgutil.get_data('bes', filename)
      dst_path = path.join(where, filename)
      file_util.save(dst_path, content = content, mode = 0o755)
      if file_util.read(dst_path) != content:
        raise RuntimeError('Failed to save %s to %s.' % (filename, dst_path))
