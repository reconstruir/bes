#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import codecs, hashlib
import os.path as path, os, platform, shutil, tempfile
from bes.common import check, object_util, string_util
from bes.system import compat, log

class file_util(object):

  @classmethod
  def mkdir(clazz, p, mode = None):
    if path.isdir(p):
      return
    os.makedirs(p)
    if mode:
      os.chmod(p, mode)
                  
  @classmethod
  def ensure_file_dir(clazz, p, mode = None):
    d = path.dirname(p)
    if d:
      clazz.mkdir(d, mode = mode)
      
  @classmethod
  def remove(clazz, files):
    files = object_util.listify(files)
    for f in files:
      try:
        if path.isdir(f):
          shutil.rmtree(f)
        else:
          os.remove(f)
      except Exception as ex:
        clazz.log_d('Caught exception %s removing %s' % (ex, f))
        pass

  @classmethod
  def save(clazz, filename, content = None, mode = None, codec = 'utf-8'):
    'Atomically save content to filename using an intermediate temporary file.'
    dirname, basename = os.path.split(filename)
    dirname = dirname or None
    if dirname:
      clazz.mkdir(path.dirname(filename))
    tmp = tempfile.NamedTemporaryFile(prefix = basename, dir = dirname, delete = False, mode = 'wb')
    if content:
      if compat.IS_PYTHON3 and string_util.is_string(content) and codec is not None:
        content_data = codecs.encode(content, codec)
      else:
        content_data = content
      tmp.write(content_data)
    tmp.flush()
    os.fsync(tmp.fileno())
    tmp.close()
    if mode:
      os.chmod(tmp.name, mode)
    os.rename(tmp.name, filename)
    return filename

  @classmethod
  def backup(clazz, filename, suffix = '.bak'):
    'Make a backup of filename if it exists.'
    if path.exists(filename):
      if path.isfile(filename):
        clazz.copy(filename, filename + suffix)
      else:
        raise RuntimeError('Not a file: %s' % (filename))

  @classmethod
  def symlink(clazz, src, dst):
    clazz.remove(dst)
    os.symlink(src, dst)

  @classmethod
  def hard_link(clazz, src, dst):
    if not clazz.same_device_id(src, dst):
      raise IOError('%s and %s cannot be in different filesystems.' % (src, dst))
    clazz.ensure_file_dir(dst)
    if path.exists(dst):
      if path.isdir(dst):
        raise IOError('dst exists and is a directory: %s' % (dst))
      clazz.remove(dst)
    os.link(src, dst)
    
  @classmethod
  def same_device_id(clazz, src, dst):
    'Return True if src and dst have the same device id.'
    dst_dir = path.dirname(dst)
    created_dst_dir = False
    if not path.exists(dst_dir):
      created_dst_dir = True
      clazz.mkdir(dst_dir)
    result = clazz.device_id(src) == clazz.device_id(dst_dir)
    if created_dst_dir:
      os.removedirs(dst_dir)
    return result
    
  @classmethod
  def extension(clazz, filename):
    'Return the extension for filename.'
    return string_util.remove_head(path.splitext(filename)[1], os.extsep)

  @classmethod
  def remove_extension(clazz, filename):
    'Return the root of filename withouth extension.'
    return path.splitext(filename)[0]

  @classmethod
  def lstrip_sep(clazz, filename):
    'Return the filename without a leading path separator.'
    return clazz.__strip_sep(filename, True, False)

  @classmethod
  def rstrip_sep(clazz, filename):
    'Return the filename without a trailing path separator.'
    return clazz.__strip_sep(filename, False, True)

  @classmethod
  def strip_sep(clazz, filename):
    'Return the filename without either leading or trailing path separator.'
    return clazz.__strip_sep(filename, True, True)

  @classmethod
  def __strip_sep(clazz, filename, leading, trailing):
    'Return the filename without a trailing path separator.'

    leading = leading and filename.startswith(path.sep)
    trailing = trailing and filename.endswith(path.sep)
    if not leading and not trailing:
      return filename
    start = 0
    end = len(filename)
    if leading:
      start = len(path.sep)
    if trailing:
      end = -len(path.sep)
    return filename[start:end]

  @classmethod
  def ensure_rsep(clazz, filename):
    'Ensure that the given filename has a trailing separator.'
    if not filename.endswith(os.sep):
      return filename + os.sep
    return filename

  @classmethod
  def ensure_lsep(clazz, filename):
    'Ensure that the given filename has a leading separator.'
    if not filename.startswith(os.sep):
      return os.sep + filename
    return filename

  @classmethod
  def remove_head(clazz, filename, head):
    'Return filename without head.'
    head = clazz.ensure_rsep(path.normpath(head))
    result = string_util.remove_head(filename, head)
    return result

  @classmethod
  def remove_tail(clazz, filename, tail):
    'Return filename without tail.'
    tail = clazz.ensure_lsep(path.normpath(tail))
    result = string_util.remove_tail(filename, tail)
    return result

  @classmethod
  def rename(clazz, src, dst):
    d = path.dirname(dst)
    if d:
      clazz.mkdir(path.dirname(dst))
    shutil.move(src, dst)

  @classmethod
  def copy(clazz, src, dst, use_hard_link = False):
    dirname = path.dirname(dst)
    if dirname:
      clazz.mkdir(dirname)
    if use_hard_link and clazz.same_device_id(src, dst):
      clazz.hard_link(src, dst)
      return
    shutil.copy(src, dst)

  @classmethod
  def mode(clazz, filename):
    'Return only the lower bits of a inode mode (permissions)'
    return os.stat(filename).st_mode & 0o777
  
  @classmethod
  def size(clazz, filename):
    return os.stat(filename).st_size

  @classmethod
  def mtime(clazz, filename):
    return os.stat(filename).st_mtime

  @classmethod
  def copy_mode(clazz, src, dst):
    shutil.copymode(src, dst)

  @classmethod
  def read(clazz, filename, codec = None):
    'Read a file into a string.'
    with open(filename, 'rb') as f:
      content = f.read()
      if codec:
        return codecs.decode(content, codec)
      else:
        return content

  @classmethod
  def read_as_lines(clazz, filename, ignore_empty = True):
    'Read a file as a list of lines.'
    lines = clazz.read(filename).split('\n')
    if ignore_empty:
      return [ line for line in lines if line ]
    else:
      return lines
      
  @classmethod
  def make_paths_absolute(clazz, paths):
    paths = object_util.listify(paths)
    return [ clazz.ensure_abspath(p) for p in paths ]

  @classmethod
  def make_paths_relative(clazz, paths):
    paths = object_util.listify(paths)
    return [ path.relpath(p) for p in paths ]

  @classmethod
  def ensure_abspath(clazz, p):
    assert p
    if path.isabs(p):
      return p
    return path.abspath(p)

  @classmethod
  def is_broken_link(clazz, filename):
    return path.islink(filename) and not path.isfile(os.readlink(filename))

  @classmethod
  def is_empty(clazz, filename):
    return clazz.size(filename) == 0

  @classmethod
  def device_id(clazz, filename):
    return os.stat(filename).st_dev

  # https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
  @classmethod
  def sizeof_fmt(clazz, num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
      if abs(num) < 1024.0:
        return "%3.1f%s%s" % (num, unit, suffix)
      num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

  # https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
  @classmethod
  def checksum(clazz, function_name, filename, chunk_size = 1024 * 1204):
    hasher = hashlib.new(function_name)
    with open(filename, 'rb') as fin: 
      for chunk in iter(lambda: fin.read(chunk_size), b''): 
        hasher.update(chunk)
    return hasher.hexdigest()

  @classmethod
  def relocate_file(clazz, filename, dst_dir):
    new_filename = path.join(dst_dir, path.basename(filename))
    file_util.rename(filename, new_filename)
    return new_filename
  
  @classmethod
  def is_basename(clazz, filename):
    return path.basename(filename) == filename
  
log.add_logging(file_util, 'file_util')
