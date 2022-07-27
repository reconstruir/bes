#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .dir_partition_criteria_base import dir_partition_criteria_base
from .file_attributes_metadata import file_attributes_metadata
from .file_check import file_check

class dir_partition_criteria_media_type(dir_partition_criteria_base):
  
  def classify(self, filename):
    filename = file_check.check_file(filename)
    media_type = file_attributes_metadata.get_media_type(filename, fallback = True, cached = True)
    if media_type == 'unknown':
      return None
    return media_type
