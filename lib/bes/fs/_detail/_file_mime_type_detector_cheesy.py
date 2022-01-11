#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.fs.file_check import file_check
from bes.system.compat import compat
from bes.system.python import python

from ._file_mime_type_detector_base import _file_mime_type_detector_base

class _file_mime_type_detector_cheesy(_file_mime_type_detector_base):
  '''
  A very cheesy mime type detecter that is very limited to some types
  needed for bes things to work in the absolute disaster case where no
  third party mime type detector exists in the platform.
  '''

  @classmethod
  #@abstractmethod
  def is_supported(clazz):
    'Return True if this class is supported on the current platform.'
    return True
  
  @classmethod
  #@abstractmethod
  def detect_mime_type(clazz, filename):
    'Detect the mime type for file.'
    filename = file_check.check_file(filename)

    return clazz._guess_mime_type(filename)

  @classmethod
  def _guess_mime_type(clazz, filename):
    '''guess the mime type of a file.
    This is obviously bs and we need a better overall mime type strategy
    that is cross platform and doest fudge one thing a time.
    These 2 specific types are handled here because there is code in bes
    that depends on detecting these files properly and mimetypes does not
    when the extension is incorrect.
    '''
    if python.is_python_script(filename):
      return 'text/x-python'
    elif clazz._is_zip(filename):
      return 'application/zip'
    return None

  # https://en.wikipedia.org/wiki/List_of_file_signatures
  _ZIP_MAGICS = {
    ( 0x50, 0x4B, 0x03, 0x04 ),
    ( 0x50, 0x4B, 0x05, 0x06 ),
    ( 0x50, 0x4B, 0x07, 0x08 ),
  }

  # https://en.wikipedia.org/wiki/List_of_file_signatures
  _ZIP_MAGICS = {
    ( 0x50, 0x4B, 0x03, 0x04 ),
    ( 0x50, 0x4B, 0x05, 0x06 ),
    ( 0x50, 0x4B, 0x07, 0x08 ),
  }

#  # https://tukaani.org/xz/xz-file-format.txt
#  _MAGIC = b'\xfd\x37\x7a\x58\x5a\x00'
  
  @classmethod
  def _is_zip(clazz, filename):
    with open(filename, 'rb') as fin:
      data = fin.read(4)
      # FIXME: figure out this ridiculousness
      if compat.IS_PYTHON2:
        magic = ( ord(data[0]), ord(data[1]), ord(data[2]), ord(data[3]) )
      else:
        magic = ( data[0], data[1], data[2], data[3] )
      return magic in clazz._ZIP_MAGICS
