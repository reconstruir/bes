#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system.check import check
from bes.common.object_util import object_util

from .dir_util import dir_util
from .file_util import file_util
from .file_check import file_check

class dir_split(object):
  'A class to split directories'

  @classmethod
  def split(clazz, d, dst_dir, prefix, chunk_size):
    d = file_check.check_dir(d)
    check.check_string(dst_dir)
    check.check_string(prefix)
    check.check_int(chunk_size)

    files = [ f for f in dir_util.list(d) if path.isfile(f) ]
    chunks = [ chunk for chunk in object_util.chunks(files, chunk_size) ]
    num_chunks = len(chunks)
    num_digits = len(str(num_chunks))
    for i, chunk in enumerate(chunks):
      dst_basename = '{}{}'.format(prefix, str(i + 1).zfill(num_digits))
      chunk_dst_dir = path.join(dst_dir, dst_basename)
      for f in chunk:
        dst_filename = path.join(chunk_dst_dir, path.basename(f))
        file_util.rename(f, dst_filename)
