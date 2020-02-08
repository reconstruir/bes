#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
import math

from bes.common.check import check
from bes.fs.file_util import file_util
from bes.system.log import logger

class file_split(object):
  'Split a file into into pieces.'

  log = logger('file_split')
  
  @classmethod
  def split(clazz, filename, max_size):
    file_size = file_util.size(filename)
    
    clazz.log.log_d('split: filename={} max_size={} file_size={}'.format(filename,
                                                                         file_util.format_size(max_size),
                                                                         file_util.format_size(file_size)))
    
    num_total = int(math.ceil(float(file_size) / float(max_size)))
    result_file_list = []
    with open(filename, 'rb') as fin:
      index = 0
      while True:
        data = fin.read(max_size)
        if not data:
          break
        next_filename = clazz._make_split_filename(filename, index + 1, num_total)
        with open(next_filename, 'wb') as fout:
          fout.write(data)
          result_file_list.append(next_filename)
        index += 1
    return result_file_list

  @classmethod
  def _make_split_filename(clazz, filename, index, total):
    index_s = str(index).zfill(2)
    total_s = str(total).zfill(2)
    return '{}.split.{}of{}'.format(filename, index_s, total_s)
  
  @classmethod
  def unsplit(clazz, output_filename, files):
    with open(output_filename, 'wb') as fout:
      for next_filename in files:
        with open(next_filename, 'rb') as fin:
          fout.write(fin.read())
