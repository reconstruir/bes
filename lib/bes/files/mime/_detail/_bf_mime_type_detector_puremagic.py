#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger
from bes.files.bf_check import bf_check

from ._bf_mime_type_detector_base import _bf_mime_type_detector_base

class _bf_mime_type_detector_puremagic(_bf_mime_type_detector_base):

  _log = logger('_bf_mime_type_detector_puremagic')

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    try:
      import puremagic
      clazz._log.log_d(f'"import puremagic" succeeds')
      return True
    except ModuleNotFoundError as ex:
      clazz._log.log_d(f'puremagic module not found')
      pass
    return False
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = bf_check.check_file(filename)

    import puremagic
    try:
      rv = puremagic.magic_file(filename)
      clazz._log.log_d(f'rv={rv}')
      if not rv:
        clazz._log.log_d(f'rv is none')
        return None
      return clazz._find_mime_type(rv)
    except Exception as ex:
      print(f'ERROR: caught: {ex} for {filename}')
      return None

  @classmethod
  def _find_mime_type(clazz, puremagic_result):
    'Find the best puremagic result entry.'
    puremagic_result = puremagic_result or []
    for entry in puremagic_result:
      if entry.mime_type:
        return entry.mime_type
    return None
