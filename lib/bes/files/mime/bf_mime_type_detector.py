#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.files.bf_check import bf_check

from ._detail._bf_mime_type_detector_base import _bf_mime_type_detector_base
from ._detail._bf_mime_type_detector_cheesy  import _bf_mime_type_detector_cheesy
from ._detail._bf_mime_type_detector_filetype  import _bf_mime_type_detector_filetype
from ._detail._bf_mime_type_detector_puremagic  import _bf_mime_type_detector_puremagic

class bf_mime_type_detector(_bf_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    return True

  _ALL_DETECTORS = [
    _bf_mime_type_detector_filetype,
    _bf_mime_type_detector_cheesy,
    _bf_mime_type_detector_puremagic,
  ]
  _POSSIBLE_DETECTORS = [ p for p in _ALL_DETECTORS if p.is_supported() ]

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
    return mime_type
