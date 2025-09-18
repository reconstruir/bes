#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import contextlib, codecs, errno, subprocess
import os.path as path, os, shutil, sys, tempfile
import locale

from ..common.object_util import object_util
from ..system.check import check
from ..system.compat import compat
from ..system.env_var import os_env_var
from ..system.filesystem import filesystem
from ..system.which import which

from .bf_check import bf_check

class bf_file_ops(object):

  @classmethod
  def mkdir(clazz, p, mode = None):
    try:
      os.makedirs(p)
    except OSError as ex:
      if ex.errno != errno.EEXIST:
        raise
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
    filesystem.remove(files, raise_not_found_error = False)

  @classmethod
  def save(clazz, filename, content = None, perm = None, encoding = None):
    'Atomically save content to filename using an intermediate temporary file.'
    check.check_string(filename)
    check.check_int(perm, allow_none = True)

    open_mode = None
    if content != None:
      if check.is_string(content):
        open_mode = 'w+t'
        encoding = check.check_string(encoding, allow_none = True) or locale.getpreferredencoding()
      elif check.is_bytes(content):
        open_mode = 'w+b'
        if encoding:
          raise ValueError(f'encoding should be None when the content is bytes')
        encoding = None
      else:
        raise TypeError(f'content should be None, string or bytes: "{content}" - {type(content)}')
    if not open_mode:
      open_mode = 'w+t'
      
    dirname, basename = os.path.split(filename)
    dirname = dirname or None
    if dirname:
      clazz.mkdir(path.dirname(filename))
#    if path.exists(filename):
#      clazz.remove(filename)
    tmp = tempfile.NamedTemporaryFile(prefix = basename, dir = dirname, delete = False, mode = open_mode, encoding = encoding)
    if content:
      tmp.write(content)
    tmp.flush()
    os.fsync(tmp.fileno())
    tmp.close()
    if perm:
      os.chmod(tmp.name, perm)
    clazz._cross_device_safe_rename(tmp.name, filename)
    return filename

  @classmethod
  def save_text(clazz, filename, text, perm = None, encoding = None):
    'Atomically save text to filename using an intermediate temporary file.'
    check.check_string(filename)
    check.check_string(text)
    check.check_int(perm, allow_none = True)
    check.check_string(encoding, allow_none = True)

    encoding = encoding or locale.getpreferredencoding()
    encoded_text = text.encode(encoding)
    
    dirname, basename = os.path.split(filename)
    dirname = dirname or None
    if dirname:
      clazz.mkdir(path.dirname(filename))
    tmp = tempfile.NamedTemporaryFile(prefix = basename, dir = dirname, delete = False, mode = 'wb')
    tmp.write(encoded_text)
    tmp.flush()
    os.fsync(tmp.fileno())
    tmp.close()
    if perm:
      os.chmod(tmp.name, perm)
    clazz._cross_device_safe_rename(tmp.name, filename)
    return filename

  @classmethod
  def read_text(clazz, filename, encoding = None):
    'Read text with binary mode and decode to gurantee line endings dont get screwed.'
    bf_check.check_file(filename)
    check.check_string(encoding, allow_none = True)

    encoding = encoding or locale.getpreferredencoding()

    with open(filename, 'rb') as f:
      encoded_content = f.read()
      f.flush()
      content = encoded_content.decode(encoding)
      return content
  
  @classmethod
  def _cross_device_safe_rename(clazz, src, dst):
    'Rename that deals with cross device link issues.' 
    try:
      try:
        os.rename(src, dst)
      except FileExistsError as fex:
        filesystem.remove(dst)
        os.rename(src, dst)
    except OSError as ex:
      if ex.errno == errno.EXDEV:
        shutil.move(src, dst)
      else:
        raise
  
  @classmethod
  def backup(clazz, filename, suffix = '.bak'):
    'Make a backup of filename if it exists.'
    if not path.exists(filename):
      return
    if not path.isfile(filename):
      raise RuntimeError(f'Not a file: {filename}')

    backup_filename = filename + suffix
    # if the backup file exists and its the same dont touch it
    if path.exists(backup_filename) and clazz.files_are_the_same(filename, backup_filename):
      return
    clazz.copy(filename, backup_filename)

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
  def rename(clazz, src, dst):
    d = path.dirname(dst)
    if d:
      clazz.mkdir(path.dirname(dst))
    shutil.move(src, dst)

  @classmethod
  def copy(clazz, src, dst, use_hard_link = False):
    if src == dst:
      raise IOError('src and dst files are the same: "{}"'.format(src))
    dirname = path.dirname(dst)
    if dirname:
      clazz.mkdir(dirname)
    if use_hard_link and clazz.same_device_id(src, dst):
      clazz.hard_link(src, dst)
      return
    shutil.copy(src, dst)

  @classmethod
  def copy_mode(clazz, src, dst):
    shutil.copymode(src, dst)

  @classmethod
  def read(clazz, filename, encoding = None):
    'Read a file into a string.'
    if encoding:
      return clazz.read_text(filename, encoding = encoding)
    else:
      with open(filename, 'rb') as f:
        return f.read()

  @classmethod
  def read_as_lines(clazz, filename, encoding = 'utf-8', ignore_empty = True):
    'Read a file as a list of lines.'
    lines = clazz.read(filename, encoding = encoding).split(os.sep)
    if ignore_empty:
      return [ line for line in lines if line ]
    else:
      return lines

  @classmethod
  def relocate_file(clazz, filename, dst_dir):
    new_filename = path.join(dst_dir, path.basename(filename))
    file_util.rename(filename, new_filename)
    return new_filename
  
  @classmethod
  @contextlib.contextmanager
  def open_with_default(clazz, filename = None, mode = None):
    '''
    Return an open file managed with contextmanager or sys.stdout if None
    From: https://stackoverflow.com/a/17603000
    '''
    mode = mode or 'w'
    if filename and filename != '-':
      fh = open(filename, mode)
      using_stdout = False
    else:
      fh = os.fdopen(sys.stdout.fileno(), mode, closefd = False)
      using_stdout = True
    try:
      yield fh
    finally:
      if not using_stdout:
        fh.close()

  @classmethod
  def page(clazz, filename):
    'Page a file with ${PAGER}'
    bf_check.check_file(filename)

    if not path.exists(filename):
      raise RuntimeError('Not found: "{}"'.format(filename))
    v = os_env_var('PAGER')
    if v.is_set:
      pager = which.which(v.value)
    else:
      pager = which.which('less') or which.which('more')
    if not pager:
      raise RuntimeError('Pager not found')
    subprocess.call([ pager, filename ])

  @classmethod
  def files_are_the_same(clazz, filename1, filename2, read_size = 1024 * 1024):
    filename1 = bf_check.check_file(filename1)
    filename2 = bf_check.check_file(filename2)

    if os.stat(filename1).st_size != os.stat(filename2).st_size:
      return False

    with open(filename1, 'rb') as f1:
      with open(filename2, 'rb') as f2:
        if f1.read(read_size) != f2.read(read_size):
          return False
    return True
