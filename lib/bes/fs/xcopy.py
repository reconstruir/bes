#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os, re
from bes.system.execute import execute

from .file_util import file_util
from .temp_file import temp_file

class xcopy(object):

  @classmethod
  def copy_tree(clazz, src_dir, dst_dir, excludes = None):
    excludes = excludes or []
    if not path.isdir(src_dir):
      raise RuntimeError('src_dir is not a directory: %s' % (src_dir))
    file_util.mkdir(dst_dir)
    cmd = [
      'xcopy',
      '"{}"'.format(src_dir),
      '"{}"'.format(dst_dir),
      '/q', # Suppresses the display of xcopy messages.
      '/e', # Copies all subdirectories, even if they are empty
      '/k', # Copies all subdirectories, even if they are empty
      '/h', # Copies files with hidden and system file attributes. By default, xcopy does not copy hidden or system files
      '/r', # Copies read-only files.
      '/y', # Suppresses prompting to confirm that you want to overwrite an existing destination file.
    ]
    if excludes:
      content = '\r\n'.join(excludes)
      excludes_filename = temp_file.make_temp_file(content = content)
      cmd.append('/exclude:{}'.format(excludes_filename))
    execute.execute(cmd, shell = True)
