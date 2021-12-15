#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host

HAS_MAGIC = False
try:
  import magic
  HAS_MAGIC = True
except ModuleNotFoundError as ex:
  pass

HAS_PUREMAGIC = False
try:
  import puremagic
  HAS_PUREMAGIC = True
except ModuleNotFoundError as ex:
  pass

#HAS_MAGIC = False
#HAS_PUREMAGIC = False
#print('HAS_MAGIC={} HAS_PUREMAGIC={}'.format(HAS_MAGIC, HAS_PUREMAGIC))

if HAS_MAGIC:
  from ._detail._file_mime_type_detector_magic import _file_mime_type_detector_magic as _file_mime_type_detector_super_class
elif HAS_PUREMAGIC:
  from ._detail._file_mime_type_detector_puremagic import _file_mime_type_detector_puremagic as _file_mime_type_detector_super_class
elif host.is_unix():
  from ._detail._file_mime_type_detector_file_exe import _file_mime_type_detector_file_exe as _file_mime_type_detector_super_class
elif host.SYSTEM == host.WINDOWS:
  from ._detail._file_mime_type_detector_mimetypes import _file_mime_type_detector_mimetypes as _file_mime_type_detector_super_class
else:
  host.raise_unsupported_system()

class file_mime_type_detector(_file_mime_type_detector_super_class):
  pass
