#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import os

class vfs_file_find(object):

  #: https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
  @classmethod
  def walk_with_depth(clazz, root_dir, max_depth = None, follow_links = False):
    root_dir = root_dir.rstrip(path.sep)
    if not path.isdir(root_dir):
      raise RuntimeError('not a directory: %s' % (root_dir))
    num_sep = root_dir.count(path.sep)
    for root, dirs, files in os.walk(root_dir, topdown = True, followlinks = follow_links):
      #print(" root: %s" % (root))
      #print(" dirs: %s" % (' '.join(dirs)))
      #print("files: %s" % (' '.join(files)))
      #print("")
      yield root, dirs, files
      num_sep_this = root.count(path.sep)
      if max_depth is not None:
        if num_sep + max_depth - 1 <= num_sep_this:
          del dirs[:]
