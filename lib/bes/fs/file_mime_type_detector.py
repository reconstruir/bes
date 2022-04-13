#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.fs.file_check import file_check

from ._detail._file_mime_type_detector_base import _file_mime_type_detector_base
from ._detail._file_mime_type_detector_cheesy  import _file_mime_type_detector_cheesy
from ._detail._file_mime_type_detector_file_exe  import _file_mime_type_detector_file_exe
from ._detail._file_mime_type_detector_magic  import _file_mime_type_detector_magic
from ._detail._file_mime_type_detector_mimetypes  import _file_mime_type_detector_mimetypes
from ._detail._file_mime_type_detector_puremagic  import _file_mime_type_detector_puremagic

class file_mime_type_detector(_file_mime_type_detector_base):

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    return True

  _POSSIBLE = [
    _file_mime_type_detector_magic,
    _file_mime_type_detector_puremagic,
    _file_mime_type_detector_cheesy,
    _file_mime_type_detector_file_exe,
    _file_mime_type_detector_mimetypes,
  ]
  _POSSIBLE = [ p for p in _POSSIBLE if p.is_supported() ]
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = file_check.check_file(filename)

    for p in clazz._POSSIBLE:
      mime_type = p.detect_mime_type(filename)
      if mime_type:
        return mime_type
    return None

#####from bes.system.host import host
#####
#####HAS_MAGIC = False
#####try:
#####  import magic
#####  HAS_MAGIC = True
#####except ModuleNotFoundError as ex:
#####  pass
#####
#####HAS_PUREMAGIC = False
#####try:
#####  import puremagic
#####  HAS_PUREMAGIC = True
#####except ModuleNotFoundError as ex:
#####  pass
#####
######HAS_MAGIC = False
######HAS_PUREMAGIC = False
######print('HAS_MAGIC={} HAS_PUREMAGIC={}'.format(HAS_MAGIC, HAS_PUREMAGIC))
#####
#####if HAS_MAGIC:
#####  from ._detail._file_mime_type_detector_magic import _file_mime_type_detector_magic as _file_mime_type_de#####tector_super_class
#####elif HAS_PUREMAGIC:
#####  from ._detail._file_mime_type_detector_puremagic import _file_mime_type_detector_puremagic as _file_mime_type_detector_super_class
#####elif host.is_unix():
#####  from ._detail._file_mime_type_detector_file_exe import _file_mime_type_detector_file_exe as _file_mime_type_detector_super_class
#####elif host.SYSTEM == host.WINDOWS:
#####  from ._detail._file_mime_type_detector_mimetypes import _file_mime_type_detector_mimetypes as _file_mime_type_detector_super_class
#####else:
#####  host.raise_unsupported_system()
#####
#####class file_mime_type_detector(_file_mime_type_detector_super_class):
#####  pass
