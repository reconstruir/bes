#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.system.check import check
from bes.system.log import logger
from bes.common.object_util import object_util
from bes.common.string_util import string_util

from .dir_split_options import dir_split_options
from .dir_util import dir_util
from .file_check import file_check
from .file_util import file_util

class dir_split(object):
  'A class to split directories'

  _log = logger('dir_split')

  @classmethod
  def split(clazz, src_dir, dst_dir, options = None):
    d = file_check.check_dir(src_dir)
    check.check_string(dst_dir)
    check.check_dir_split_options(options, allow_none = True)

    options = options or dir_split_options()
    info = clazz._split_info(src_dir, dst_dir, options = options)
    for item in info.items:
      file_util.rename(item.src_filename, item.dst_filename)

    for d in info.existing_split_dirs:
      if dir_util.is_empty(d):
        file_util.remove(d)

  _split_item = namedtuple('_split_item', 'src_filename, dst_filename')
  _split_items_info = namedtuple('_split_items_info', 'items, existing_split_dirs')
  @classmethod
  def _split_info(clazz, src_dir, dst_dir, options = None):
    d = file_check.check_dir(src_dir)
    check.check_string(dst_dir)
    check.check_dir_split_options(options, allow_none = True)

    old_files = []
    existing_split_dirs = clazz._existing_split_dirs(dst_dir, options.prefix)
    for old_dir in existing_split_dirs:
      old_files.extend(dir_util.list_files(old_dir))
    clazz._log.log_d('old_files={}'.format(old_files))
    
    options = options or dir_split_options()
    items = []
    new_files = dir_util.list_files(src_dir)
    files = old_files + new_files
    chunks = [ chunk for chunk in object_util.chunks(files, options.chunk_size) ]
    num_chunks = len(chunks)
    num_digits = len(str(num_chunks))
    for i, chunk in enumerate(chunks):
      dst_basename = '{}{}'.format(options.prefix, str(i + 1).zfill(num_digits))
      chunk_dst_dir = path.join(dst_dir, dst_basename)
      for f in chunk:
        dst_filename = path.join(chunk_dst_dir, path.basename(f))
        items.append(clazz._split_item(f, dst_filename))
    return clazz._split_items_info(items, existing_split_dirs)

  @classmethod
  def split_items(clazz, src_dir, dst_dir, options = None):
    'Return a list of split items that when renaming each item implements split.'
    info = clazz._split_info(src_dir, dst_dir, options = options)
    return info.items
  
  @classmethod
  def _existing_split_dirs(clazz, dst_dir, prefix):
    if not path.isdir(dst_dir):
      return []
    return dir_util.list_dirs(dst_dir, patterns = '*{}{}*'.format(path.sep, prefix))

  @classmethod
  def _existing_split_dirs_common_num_digits(clazz, dirs, prefix):
    basenames = [ path.basename(f) for f in dirs ]
    #clazz._log.log_d('basenames={}'.format(basenames))
    without_prefices = [ string_util.remove_head(f, prefix) for f in basenames ]
    #clazz._log.log_d('without_prefices={}'.format(without_prefices))
    lengths = list(set([ len(f) for f in without_prefices ]))
    if len(lengths) == 1:
      return lengths[0]
    return None
  
