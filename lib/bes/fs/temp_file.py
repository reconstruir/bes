#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.filesystem import filesystem
from ..system.check import check

import os, os.path as path, sys, tempfile
import pty

from .file_util import file_util

class temp_item(namedtuple('temp_item', 'filename, content, mode')):
  'Description of an temp item.'

  def __new__(clazz, filename, content = None, mode = None):
    return clazz.__bases__[0].__new__(clazz, filename, content, mode)

  def write(self, root_dir):
    p = path.join(root_dir, self.filename)
    if path.isfile(self.content):
      content = file_util.read(self.content)
    else:
      content = self.content
    file_util.save(p, content = content, mode = self.mode)
    
class temp_file(object):

  _DEFAULT_PREFIX = path.splitext(path.basename(sys.argv[0]))[0] + '-tmp-'

  @classmethod
  def make_temp_file(clazz, content = None, prefix = None, suffix = None, dir = None, mode = 'w+b',
                     delete = True, perm = None, non_existent = False):
    'Write content to a temporary file.  Returns the file object.'
    prefix = prefix or clazz._DEFAULT_PREFIX
    suffix = suffix or ''
    if dir and not path.isdir(dir):
      file_util.mkdir(dir)
    tmp = tempfile.NamedTemporaryFile(prefix = prefix,
                                      suffix = suffix,
                                      dir = dir,
                                      mode = mode,
                                      delete = False)
    if content:
      if check.is_string(content):
        if path.isfile(content):
          with open(content, 'rb') as f:
            content = f.read()
        else:
          content = content.encode('utf-8')
      elif not isinstance(content, bytes):
        content = content.encode('utf-8')
      tmp.write(content)
    tmp.flush()
    if perm:
      os.chmod(tmp.name, perm)
    os.fsync(tmp.fileno())
    if delete:
      filesystem.atexit_remove(tmp.name)
    tmp.close()
    if non_existent:
      file_util.remove(tmp.name)
    return tmp.name

  @classmethod
  def make_temp_dir(clazz, prefix = None, suffix = None, dir = None,
                    delete = True, items = None, non_existent = False):
    'Make a temporary directory.'
    prefix = prefix or clazz._DEFAULT_PREFIX
    suffix = suffix or '.dir'
    if dir and not path.isdir(dir):
      file_util.mkdir(dir)
    tmp_dir = tempfile.mkdtemp(prefix = prefix, suffix = suffix, dir = dir)
    assert path.isdir(tmp_dir)
    if items:
      assert not non_existent
      clazz.write_temp_files(tmp_dir, items)
    if non_existent:
      file_util.remove(tmp_dir)
    if delete:
      filesystem.atexit_remove(tmp_dir)
    return tmp_dir

  @classmethod
  def make_named_temp_file(clazz, filename, content = None, delete = True, perm = None):
    'Write a named temporary file to an also temporary directory.'
    tmp_dir = clazz.make_temp_dir(delete = delete)
    tmp_file = path.join(tmp_dir, filename)
    file_util.save(tmp_file, content = content)
    if perm:
      os.chmod(tmp_file, perm)
    return tmp_file
  
  @classmethod
  def atexit_delete(clazz, filename):
    'Delete filename atexit time.'
    filesystem.atexit_remove(filename)

  @classmethod
  def write_temp_files(clazz, root_dir, items):
    'Write a sequence of temp files specified by items.'
    for item in items:
      item.write(root_dir)

  @classmethod
  def make_temp_chardev(clazz):
    master_fd, slave_fd = pty.openpty()
    real_path = os.ttyname(slave_fd)
    return real_path
