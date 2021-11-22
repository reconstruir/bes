#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.system.check import check
from bes.common.object_util import object_util

from .dir_split_options import dir_split_options
from .dir_util import dir_util
from .file_check import file_check
from .file_util import file_util

class dir_split(object):
  'A class to split directories'

  @classmethod
  def split(clazz, src_dir, dst_dir, options = None):
    d = file_check.check_dir(src_dir)
    check.check_string(dst_dir)
    check.check_dir_split_options(options, allow_none = True)

    options = options or dir_split_options()
    items = clazz.split_items(src_dir, dst_dir, options = options)
    for item in items:
      file_util.rename(item.src_filename, item.dst_filename)

  _split_item = namedtuple('_split_item', 'src_filename, dst_filename')
  @classmethod
  def split_items(clazz, src_dir, dst_dir, options = None):
    'Return a list of split items that when renaming each item implements split.'
    d = file_check.check_dir(src_dir)
    check.check_string(dst_dir)
    check.check_dir_split_options(options, allow_none = True)

    options = options or dir_split_options()
    result = []
    files = [ f for f in dir_util.list(src_dir) if path.isfile(f) ]
    chunks = [ chunk for chunk in object_util.chunks(files, options.chunk_size) ]
    num_chunks = len(chunks)
    num_digits = len(str(num_chunks))
    for i, chunk in enumerate(chunks):
      dst_basename = '{}{}'.format(options.prefix, str(i + 1).zfill(num_digits))
      chunk_dst_dir = path.join(dst_dir, dst_basename)
      for f in chunk:
        dst_filename = path.join(chunk_dst_dir, path.basename(f))
        result.append(clazz._split_item(f, dst_filename))
    return result
