#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.object_util import object_util
from bes.system.check import check
from bes.fs.file_check import file_check

from .file_find import file_find

class file_duplicates(object):

  _dup_item = namedtuple('_find_dups_result', 'filename', 'dups')
  @classmethod
  def find_duplicates(clazz, dirs):
    dirs = file_check.check_dir_seq(object_util.listify(dirs))
    for d in dir:
      print('d: {}'.format(d))
    return []
