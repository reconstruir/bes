#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, os, re
from bes.system.execute import execute
from bes.system.which import which

from .file_util import file_util
from .temp_file import temp_file

class xcopy(object):

  @classmethod
  def copy_tree(clazz, src_dir, dst_dir, excludes = None):
    excludes = excludes or []
    if not path.isdir(src_dir):
      raise RuntimeError('src_dir is not a directory: %s' % (src_dir))
    file_util.mkdir(dst_dir)
    xcopy_exe = which.which('robocopy.exe')
    cmd = [
      xcopy_exe,
      '"{}"'.format(src_dir),
      '"{}"'.format(dst_dir),
      '/E', # Copies all subdirectories, even if they are empty
    ]
    if excludes:
      for exclude in excludes:
        cmd.extend([ '/XF', '"{}"'.format(exclude) ])
    rv = execute.execute(cmd,
                         shell = True,
                         raise_error = False,
                         stderr_to_stdout = True)
    if rv.exit_code >= 0 and rv.exit_code <= 7:
      return
    raise RuntimError('robocopy failed: "{}" - {}'.format(' '.join(cmd), str(rv.stdout)))
