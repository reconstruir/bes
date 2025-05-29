#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.files.bf_check import bf_check

from ._detail._bf_mime_type_detector_base import _bf_mime_type_detector_base
from ._detail._bf_mime_type_detector_cheesy  import _bf_mime_type_detector_cheesy
from ._detail._bf_mime_type_detector_file_exe  import _bf_mime_type_detector_file_exe
from ._detail._bf_mime_type_detector_magic  import _bf_mime_type_detector_magic
from ._detail._bf_mime_type_detector_mimetypes  import _bf_mime_type_detector_mimetypes
from ._detail._bf_mime_type_detector_puremagic  import _bf_mime_type_detector_puremagic

class bf_mime_type_detector(_bf_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    return True

  _ALL_DETECTORS = [
    _bf_mime_type_detector_magic,
    _bf_mime_type_detector_cheesy,
    _bf_mime_type_detector_puremagic,
    _bf_mime_type_detector_file_exe,
    _bf_mime_type_detector_mimetypes,
  ]
  _POSSIBLE_DETECTORS = [ p for p in _ALL_DETECTORS if p.is_supported() ]
  _FILE_EXE_SUPPORTED = _bf_mime_type_detector_file_exe in _POSSIBLE_DETECTORS
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = bf_check.check_file(filename)

    mime_type = None
    for next_detector in clazz._POSSIBLE_DETECTORS:
      mime_type = next_detector.detect_mime_type(filename)
      if mime_type:
        break
    if mime_type in ( 'application/octet-stream', ):
      if clazz._FILE_EXE_SUPPORTED:
        mime_type = _bf_mime_type_detector_file_exe.detect_mime_type(filename)
    return mime_type
