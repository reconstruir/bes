#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys, warnings

from bes.common.check import check
from bes.fs.file_check import file_check

from ._file_mime_type_detector_base import _file_mime_type_detector_base

class _file_mime_type_detector_magic(_file_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    try:
      if sys.version_info.major == 3 and sys.version_info.minor >= 8:
        warnings.filterwarnings('ignore', category = SyntaxWarning)
      import magic
      if sys.version_info.major == 3 and sys.version_info.minor >= 8:
        warnings.resetwarnings()
      return True
    except ModuleNotFoundError as ex:
      pass
    return False
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = file_check.check_file(filename)

    import magic
    rv = magic.from_file(filename, mime = True)
    if not rv:
      return None
    return rv
