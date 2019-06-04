#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, pkgutil
from bes.fs.file_util import file_util

class shell_framework(object):

  _FILENAME = 'env/bes_shell.sh'

  @classmethod
  def extract(clazz, where):
    python_module_name = 'bes'
    content = pkgutil.get_data('bes', clazz._FILENAME).decode('utf-8')
    dst_path = path.join(where, path.basename(clazz._FILENAME))
    file_util.save(dst_path, content = content, mode = 0o755)
    if file_util.read(dst_path, codec = 'utf8') != content:
      raise RuntimeError('Failed to save %s.' % (dst_path))
