#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import logger
from bes.files.bf_check import bf_check

from ._bf_mime_type_detector_base import _bf_mime_type_detector_base

class _bf_mime_type_detector_filetype(_bf_mime_type_detector_base):

  _log = logger('_bf_mime_type_detector_filetype')

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    try:
      import filetype
      clazz._log.log_d(f'"import filetype" succeeds')
      return True
    except ModuleNotFoundError as ex:
      clazz._log.log_d(f'filetype module not found')
      pass
    return False

  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = bf_check.check_file(filename)

    import filetype
    try:
      kind = filetype.guess(filename)
      clazz._log.log_d(f'kind={kind}')
      if kind is None:
        clazz._log.log_d(f'kind is None')
        return None
      return kind.mime
    except Exception as ex:
      clazz._log.log_d(f'caught: {ex} for {filename}')
      return None
