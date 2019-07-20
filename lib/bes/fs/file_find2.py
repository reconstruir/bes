#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import errno, os.path as path, os, stat

from bes.system.log import log
from file_util.file_util import file_util
from file_match.file_match import file_match
from temp_file import temp_file

class file_find2(object):

  FILE = 0x02
  DIR = 0x04
  LINK = 0x08
  DEVICE = 0x10
  ANY = FILE|DIR|LINK|DEVICE
  
  @classmethod
  def find(clazz, root_dir, relative = True, min_depth = None, max_depth = None, file_type = FILE):
    print("find2: root_dir=%s  min=%s  max=%s  type=%d" % (root_dir, min_depth, max_depth, file_type))

    if max_depth and min_depth and not (max_depth >= min_depth):
      raise RuntimeError('max_depth needs to be >= min_depth.')

    if min_depth and min_depth < 1:
      raise RuntimeError('min_depth needs to be >= 1.')

    def _in_range(depth, min_depth, max_depth):
      if min_depth and max_depth:
        return depth >= min_depth and depth <= max_depth
      elif min_depth:
        return depth >= min_depth
      elif max_depth:
        return depth <= max_depth
      else:
        return True
      
    def _in_range(depth, min_depth, max_depth):
      if min_depth and max_depth:
        return depth >= min_depth and depth <= max_depth
      elif min_depth:
        return depth >= min_depth
      elif max_depth:
        return depth <= max_depth
      else:
        return True
      
    result = []

    root_dir = path.normpath(root_dir)
    root_dir_count = root_dir.count(os.sep)

    for root, dirs, files in clazz._walk_with_depth(root_dir, max_depth = max_depth):
      to_check = []
      if clazz._want_file_type(file_type, clazz.FILE | clazz.LINK | clazz.DEVICE):
        to_check += files
      if clazz._want_file_type(file_type, clazz.DIR):
        to_check += dirs
      else:
        links = [ d for d in dirs if path.islink(path.normpath(path.join(root, d))) ]
        to_check += links
      for name in to_check:
        f = path.normpath(path.join(root, name))
        depth = f.count(os.sep) - root_dir_count
        if _in_range(depth, min_depth, max_depth):
          if clazz._match_file_type(f, file_type):
            if relative:
              result.append(file_util.remove_head(f, root_dir))
            else:
              result.append(f)
    return sorted(result)

  #: https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
  @classmethod
  def _walk_with_depth(clazz, root_dir, max_depth = None):
    root_dir = root_dir.rstrip(path.sep)
    if not path.isdir(root_dir):
      raise RuntimeError('not a directory: %s' % (root_dir))
    num_sep = root_dir.count(path.sep)
    for root, dirs, files in os.walk(root_dir, topdown = True):
      yield root, dirs, files
      num_sep_this = root.count(path.sep)
      if max_depth is not None:
        if num_sep + max_depth - 1 <= num_sep_this:
          del dirs[:]

  @classmethod
  def _want_file_type(clazz, file_type, mask):
    return (file_type & mask) != 0

  @classmethod
  def _match_file_type(clazz, filename, file_type):
    want_file = clazz._want_file_type(file_type, clazz.FILE)
    want_dir = clazz._want_file_type(file_type, clazz.DIR)
    want_link = clazz._want_file_type(file_type, clazz.LINK)
    want_device = clazz._want_file_type(file_type, clazz.DEVICE)
    try:
      st = os.lstat(filename)
    except OSError as ex:
      if ex.errno == errno.EBADF:
        # Some devices on macos result in bad access when trying to stat so ignore them
        return False
      else:
        raise
    is_file = stat.S_ISREG(st.st_mode)
    is_dir = stat.S_ISDIR(st.st_mode)
    is_device = stat.S_ISBLK(st.st_mode) or stat.S_ISCHR(st.st_mode)
    is_link = stat.S_ISLNK(st.st_mode)
    return (want_file and is_file) or (want_dir and is_dir) or (want_link and is_link) or (want_device and is_device)
    
  @classmethod
  def find_function(clazz, root_dir, function,
                    relative = True, min_depth = None, max_depth = None,
                    file_type = FILE):
    assert function
    result = clazz.find(root_dir, relative = relative, min_depth = min_depth,
                        max_depth = max_depth, file_type = file_type)
    return [ f for f in result if function(f) ]

  @classmethod
  def find_fnmatch(clazz, root_dir, patterns, match_type = file_match.ANY,
                   relative = True, min_depth = None, max_depth = None,
                   file_type = FILE):
    assert patterns
    assert match_type
    result = clazz.find(root_dir, 
                        relative = relative,
                        min_depth = min_depth,
                        max_depth = max_depth,
                        file_type = file_type)
    if not patterns:
      return result
    return file_match.match_fnmatch(result, patterns, match_type)

  @classmethod
  def find_re(clazz, root_dir, expressions, match_type,
              relative = True, min_depth = None, max_depth = None,
              file_type = FILE):
    assert expressions
    assert match_type
    assert key
    result = clazz.find(root_dir,
                        relative = relative,
                        min_depth = min_depth,
                        max_depth = max_depth,
                        file_type = file_type)
    if not expressions:
      return result
    return file_match.match_re(result, expressions, match_type)

  @classmethod
  def find_dirs(clazz, root_dir, relative = True, min_depth = None, max_depth = None):
    return clazz.find(root_dir, relative = relative, min_depth = min_depth,  max_depth = max_depth, file_type = clazz.DIR)

log.add_logging(file_find2, 'file_find2')
