#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.files.bf_check import bf_check
from bes.files.bf_entry import bf_entry

from ._bf_mime_type_detector_base import _bf_mime_type_detector_base

class _bf_mime_type_detector_attributes(_bf_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    return True
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = bf_check.check_file(filename)
    entry = bf_entry(filename)
    return entry.mime_type
