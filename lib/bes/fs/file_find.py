#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import errno, os.path as path, os, stat

from .dir_util import dir_util
from .file_match import file_match
from .file_path import file_path
from .file_util import file_util

class file_find(object):

  FILE = 0x02
  DIR = 0x04
  LINK = 0x08
  DEVICE = 0x10
  ANY = FILE | DIR | LINK | DEVICE
  FILE_OR_LINK = FILE | LINK
  
  @classmethod
  def find(clazz, root_dir, relative = True, min_depth = None,
           max_depth = None, file_type = FILE, follow_links = False,
           match_patterns = None, match_type = None, match_basename = True,
           match_function = None, match_re = None):
    
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
      
    result = []

    root_dir = path.normpath(root_dir)
    root_dir_count = root_dir.count(os.sep)

    for root, dirs, files in clazz.walk_with_depth(root_dir, max_depth = max_depth, follow_links = follow_links):
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
              
    if match_patterns:
      result = file_match.match_fnmatch(result,
                                        match_patterns,
                                        match_type = match_type,
                                        basename = match_basename)
      
    if match_function:
      result = file_match.match_function(result,
                                         match_function,
                                         match_type = match_type,
                                         basename = match_basename)

    if match_re:
      result = file_match.match_re(result,
                                   match_re,
                                   match_type = match_type,
                                   basename = match_basename)
      
    return sorted(result)

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
                    file_type = FILE, follow_links = False, match_basename = True):
    assert callable(function)
    return clazz.find(root_dir, relative = relative, min_depth = min_depth,
                      max_depth = max_depth, file_type = file_type, follow_links = follow_links,
                      match_function = function, match_basename = match_basename)

  @classmethod
  def find_fnmatch(clazz, root_dir, patterns, match_type = file_match.ANY,
                   relative = True, min_depth = None, max_depth = None,
                   file_type = FILE, follow_links = False, match_basename = True):
    assert patterns
    assert match_type
    return clazz.find(root_dir, relative = relative, min_depth = min_depth,
                      max_depth = max_depth, file_type = file_type, follow_links = follow_links,
                      match_patterns = patterns, match_type = match_type, match_basename = match_basename)

  @classmethod
  def find_re(clazz, root_dir, expressions, match_type = file_match.ANY,
              relative = True, min_depth = None, max_depth = None,
              file_type = FILE, follow_links = False, match_basename = True):
    assert expressions
    assert match_type
    return clazz.find(root_dir, relative = relative, min_depth = min_depth,
                      max_depth = max_depth, file_type = file_type, follow_links = follow_links,
                      match_re = expressions, match_type = match_type, match_basename = match_basename)

  @classmethod
  def find_dirs(clazz, root_dir, relative = True, min_depth = None, max_depth = None,
                follow_links = False, match_basename = True):
    return clazz.find(root_dir, relative = relative, min_depth = min_depth,  max_depth = max_depth,
                      file_type = clazz.DIR, follow_links = follow_links, match_basename = match_basename)

  @classmethod
  def find_in_ancestors(clazz, start_dir, filename):
    if path.isfile(start_dir):
      start_dir = path.dirname(start_dir)
    assert path.isdir(start_dir)
    while True:
      what = path.join(start_dir, filename)
      if path.exists(what):
        return what
      start_dir = file_path.parent_dir(start_dir)
      if path.ismount(start_dir):
        return None

  @classmethod
  def find_unreadable(clazz, d, relative = True):
    'Return files and dirs that are unreadable.'
    files = clazz.find(d, relative = relative, file_type = file_find.ANY)
    result = []
    for filename in files:
      if relative:
        filename_abs = path.join(d, filename)
      else:
        filename_abs = filename
      if not os.access(filename_abs, os.R_OK):
        result.append(filename)
    return result

  @classmethod
  def find_empty_dirs(clazz, root_dir, relative = True, min_depth = None, max_depth = None):
    return clazz.find(root_dir,
                      relative = relative,
                      file_type = clazz.DIR,
                      min_depth = min_depth,
                      max_depth = max_depth,
                      match_function = lambda f: dir_util.is_empty(f),
                      match_basename = False)

  @classmethod
  def remove_empty_dirs(clazz, root_dir, min_depth = None, max_depth = None):
    result = []
    while True:
      empties = clazz.find_empty_dirs(root_dir, relative = False, min_depth = min_depth, max_depth = max_depth)
      if not empties:
        break
      for next_empty in empties:
        dir_util.remove(next_empty)
        result.append(next_empty)
    if dir_util.is_empty(root_dir):
      dir_util.remove(root_dir)
      result.append(root_dir)
    return sorted(result)
