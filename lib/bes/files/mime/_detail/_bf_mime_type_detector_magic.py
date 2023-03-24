#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys, warnings

from bes.system.check import check
from bes.files.bf_check import bf_check
from bes.warnings.warnings_override import warnings_override

from ._bf_mime_type_detector_base import _bf_mime_type_detector_base

class _bf_mime_type_detector_magic(_bf_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    with warnings_override(clauses = '>= 3.8', action = 'ignore', category = SyntaxWarning) as _:
      try:
        import magic
        return True
      except ModuleNotFoundError as ex:
        pass
    return False
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = bf_check.check_file(filename)

    import magic
    rv = magic.from_file(filename, mime = True)
    if not rv:
      return None
    return rv
