#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from .file_util import file_util

class dir_operation_util(object):
  'A class to split directories'

  _log = logger('dir_operation_util')

  @classmethod
  def move_files(clazz, items, timestamp, count):
    for item in items:
      if file_util.move_with_duplicate(item.src_filename,
                                       item.dst_filename,
                                       f'{timestamp}-{count}'):
        count += 1
