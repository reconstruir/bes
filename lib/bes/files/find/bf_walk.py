#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

from collections import namedtuple

from bes.system.check import check
from bes.system.log import logger

class bf_walk(object):

  _log = logger('bf_walk')
  
  #: https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
  _bf_walk_item = namedtuple('_bf_walk_item', 'root, dirs, files, depth')
  @classmethod
  def walk(clazz, root_dir, max_depth = None, follow_links = False):
    root_dir = root_dir.rstrip(path.sep)
    if not path.isdir(root_dir):
      raise RuntimeError('not a directory: %s' % (root_dir))
    num_sep = root_dir.count(path.sep)
    for root, dirs, files in os.walk(root_dir, topdown = True, followlinks = follow_links):
      files[:] = sorted(files)
      dirs[:] = sorted(dirs)
      clazz._log.log_d(f'walk_with_depth: root={root} dirs={dirs} files={files}')
      #print(" root: %s" % (root))
      #print(" dirs: %s" % (' '.join(dirs)))
      #print("files: %s" % (' '.join(files)))
      #print("")
      num_sep_this = root.count(path.sep)
      depth = num_sep_this - num_sep
      yield root, dirs, files, depth
      if max_depth is not None:
        if num_sep + max_depth - 1 <= num_sep_this:
          del dirs[:]
