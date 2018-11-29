#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, pkgutil
from bes.common import string_util
from bes.fs import file_util

class shell_framework(object):

  _FILES = [
    'env/bes_framework.sh',
  ]
  
  def __init__(self):
    pass
  
  def extract(self, where, namespace):
    old_namespace = 'bes'
    new_namespace = namespace
    replacements = {
      old_namespace.lower(): new_namespace.lower(),
      old_namespace.lower() + '_': new_namespace.lower() + '_',
      old_namespace.upper(): new_namespace.upper(),
      old_namespace.upper() + '_': new_namespace.upper() + '_',
    }
    for old_filename in self._FILES:
      new_filename = string_util.replace(old_filename, replacements, word_boundary = True)
      content = pkgutil.get_data('bes', old_filename)
      content = string_util.replace(content, replacements, word_boundary = True)
      dst_path = path.join(where, path.basename(new_filename))
      file_util.save(dst_path, content = content, mode = 0o755)
      if file_util.read(dst_path) != content:
        raise RuntimeError('Failed to save %s to %s.' % (filename, dst_path))
