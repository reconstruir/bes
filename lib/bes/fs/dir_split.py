#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.system.check import check

from .dir_util import dir_util
from .file_util import file_util
from .file_check import file_check

class dir_split(object):
  'A class to split directories'

  @classmethod
  def split(clazz, d, dest_dir, prefix):
    d = file_check.check_dir(d)
    check.check_string(dest_dir)
    check.check_string(prefix)
