#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import puremagic

from bes.common.check import check
from bes.fs.file_check import file_check

from ._file_mime_type_detector_base import _file_mime_type_detector_base

class _file_mime_type_detector_puremagic(_file_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = file_check.check_file(filename)

    rv = puremagic.magic_file(filename)
    print('rv={}'.format(rv))
#    for x in rv:
#      print('X: {}'.format(rv))
    if not rv:
      return None
    return clazz._find_mime_type(rv)

  @classmethod
  def _find_mime_type(clazz, puremagic_result):
    'Find the best puremagic result entry.'
    puremagic_result = puremagic_result or []
    for entry in puremagic_result:
      if entry.mime_type:
        return entry.mime_type
    return None
