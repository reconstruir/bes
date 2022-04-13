#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.fs.file_check import file_check
from bes.fs.file_attributes_metadata import file_attributes_metadata

from ._file_mime_type_detector_base import _file_mime_type_detector_base

class _file_mime_type_detector_attributes(_file_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    return True
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = file_check.check_file(filename)

    return file_attributes_metadata.get_mime_type(filename)
