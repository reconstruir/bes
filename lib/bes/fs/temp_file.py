#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import atexit, os, os.path as path, sys, tempfile
from .file_util import file_util
from bes.common.check import check
from bes.system.log import log

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
    
check.register_class(temp_item)
    
class temp_file(object):

  _DEFAULT_PREFIX = file_util.remove_extension(path.basename(sys.argv[0])) + '-tmp-'
  _DEFAULT_SUFFIX = ''
  _DEFAULT_DIR_SUFFIX = '.dir'

  @classmethod
  def make_temp_file(clazz, content = None, prefix = None, suffix = None, dir = None, mode = 'w+b', delete = True, perm = None):
    'Write content to a temporary file.  Returns the file object.'
    prefix = prefix or clazz._DEFAULT_PREFIX
    suffix = suffix or clazz._DEFAULT_SUFFIX
    if dir and not path.isdir(dir):
      file_util.mkdir(dir)
    tmp = tempfile.NamedTemporaryFile(prefix = prefix,
                                      suffix = suffix,
                                      dir = dir,
                                      mode = mode,
                                      delete = False)
    if content:
      if not isinstance(content, bytes):
        content = content.encode('utf-8')
      tmp.write(content)
    tmp.flush()
    if perm:
      os.chmod(tmp.name, perm)
    os.fsync(tmp.fileno())
    if delete:
      clazz.atexit_delete(tmp.name)
    tmp.close()
    return tmp.name

  @classmethod
  def make_temp_dir(clazz, prefix = None, suffix = None, dir = None, delete = True, items = None):
    'Make a temporary directory.'
    prefix = prefix or clazz._DEFAULT_PREFIX
    suffix = suffix or clazz._DEFAULT_DIR_SUFFIX
    if dir and not path.isdir(dir):
      file_util.mkdir(dir)
    tmp_dir = tempfile.mkdtemp(prefix = prefix, suffix = suffix, dir = dir)
    assert path.isdir(tmp_dir)
    if items:
      clazz.write_temp_files(tmp_dir, items)
      
    if delete:
      clazz.atexit_delete(tmp_dir)
    return tmp_dir

  @classmethod
  def atexit_delete(clazz, filename):
    'Delete filename atexit time.'
    def _delete_file(*args, **kargs):
      filename = args[0]
      clazz.log_d('Removing %s atexit time.' % (filename))
      file_util.remove(filename)
    atexit.register(_delete_file, [ filename ])

  @classmethod
  def write_temp_files(clazz, root_dir, items):
    'Write a sequence of temp files specified by items.'
    for item in items:
      item.write(root_dir)
      
log.add_logging(temp_file, 'temp_file')
#log.configure('temp_file=debug')
