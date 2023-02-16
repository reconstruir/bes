#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.files.bfile_check import bfile_check
from bes.fs.file_attributes_metadata import file_attributes_metadata

from ._bfile_mime_type_detector_base import _bfile_mime_type_detector_base

class _bfile_mime_type_detector_attributes(_bfile_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    return True
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = bfile_check.check_file(filename)

    return file_attributes_metadata.get_mime_type(filename)
