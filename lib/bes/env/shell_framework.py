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
    python_module_name = 'bes'
    old_namespace = 'bes'
    new_namespace = namespace
    def _permutate(s):
      return [ s, '_' + s, s + '_', '_' + s + '_' ]
    replacements = {}
    for old, new in zip(_permutate(old_namespace), _permutate(new_namespace)):
      replacements[old.lower()] = new.lower()
      replacements[old.upper()] = new.upper()
    for old_filename in self._FILES:
      new_filename = string_util.replace(old_filename, replacements, word_boundary = True)
      content = pkgutil.get_data(python_module_name, old_filename).decode('utf-8')
      content = string_util.replace(content, replacements, word_boundary = True)
      dst_path = path.join(where, path.basename(new_filename))
      file_util.save(dst_path, content = content, mode = 0o755)
      if file_util.read(dst_path, codec = 'utf8') != content:
        raise RuntimeError('Failed to save %s to %s.' % (new_filename, dst_path))
