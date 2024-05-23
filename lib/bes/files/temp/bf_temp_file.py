#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.system.filesystem import filesystem
from bes.system.check import check

import os
import os.path as path
import sys
import tempfile

from ..bf_file_ops import bf_file_ops

from .bf_temp_item import bf_temp_item
from .bf_temp_item_list import bf_temp_item_list

class bf_temp_file(object):

  _DEFAULT_PREFIX = path.splitext(path.basename(sys.argv[0]))[0] + '-tmp-'

  @classmethod
  def make_temp_file(clazz, content = None, create = True,
                     prefix = None, suffix = None,
                     dir = None, mode = 'w+b',
                     delete = True, perm = None):
    'Write content to a temporary file.  Returns the filename.'
    check.check(content, ( str, bytes ), allow_none = True)
    check.check_bool(create)
    check.check_string(prefix, allow_none = True)
    check.check_string(suffix, allow_none = True)
    check.check_string(dir, allow_none = True)
    check.check_string(mode, allow_none = True)
    check.check_bool(delete)
    check.check_int(perm, allow_none = True)
    
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
    if not create:
      bf_file_ops.remove(tmp.name)
    return tmp.name

  @classmethod
  def make_temp_dir(clazz, prefix = None, suffix = None, dir = None,
                    delete = True, items = None, create = True):
    'Make a temporary directory.'
    prefix = prefix or clazz._DEFAULT_PREFIX
    suffix = suffix or '.dir'
    if dir and not path.isdir(dir):
      bf_file_ops.mkdir(dir)
    tmp_dir = tempfile.mkdtemp(prefix = prefix, suffix = suffix, dir = dir)
    assert path.isdir(tmp_dir)
    if items:
      assert create
      clazz.write_temp_files(tmp_dir, items)
    if not create:
      bf_file_ops.remove(tmp_dir)
    if delete:
      filesystem.atexit_remove(tmp_dir)
    return tmp_dir

  @classmethod
  def make_named_temp_file(clazz, filename, content = None, delete = True, perm = None):
    'Write a named temporary file to an also temporary directory.'
    tmp_dir = clazz.make_temp_dir(delete = delete)
    tmp_file = path.join(tmp_dir, filename)
    bf_file_ops.save(tmp_file, content = content)
    if perm:
      os.chmod(tmp_file, perm)
    return tmp_file
  
  @classmethod
  def atexit_delete(clazz, filename):
    'Delete filename atexit time.'
    filesystem.atexit_remove(filename)

  @classmethod
  def write_items(clazz, root_dir, items):
    'Write a sequence of temp files specified by items.'
    check.check_string(root_dir)
    check.check_bf_temp_item_list(items)

    items.write(root_dir)
