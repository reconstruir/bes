#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.file_check import file_check

from ._file_mime_type_detector_base import _file_mime_type_detector_base

class _file_mime_type_detector_mimetypes(_file_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    try:
      import mimetypes
      return True
    except ModuleNotFoundError as ex:
      pass
    return False
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = file_check.check_file(filename)

    import mimetypes      
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type
