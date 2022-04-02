#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from .dir_partition_criteria_base import dir_partition_criteria_base
from .file_check import file_check
from .filename_util import filename_util

class dir_partition_criteria_prefix(dir_partition_criteria_base):
  
  def classify(self, filename):
    filename = file_check.check_file(filename)

    return filename_util.prefix(path.basename(filename))
