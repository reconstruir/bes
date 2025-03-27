#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.system.check import check
from bes.files.bf_check import bf_check
from bes.system.compat import compat
from bes.system.python import python

from ._bf_mime_type_detector_base import _bf_mime_type_detector_base

class _bf_mime_type_detector_cheesy(_bf_mime_type_detector_base):
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
    filename = bf_check.check_file(filename)

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
    return clazz._guess_mime_type_with_magic_bytes(filename)

  _magic_item = namedtuple('_magic_item', 'mime_type, offset, signatures')
  _MAGIC = [
    _magic_item('application/x-xz', 0, {
      b'\xfd\x37\x7a\x58\x5a\x00',
    }),
    _magic_item('application/zip', 0, {
      b'\x50\x4b\x03\x04',
      b'\x50\x4b\x05\x06',
      b'\x50\x4b\x07\x08',
    }),
    _magic_item('image/png', 0, {
      b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a',
    }),
    _magic_item('image/jpeg', 0, {
      b'\xff\xd8\xff\xe0',
    }),
    _magic_item('video/mp4', 4, {
      b'\x66\x74\x79\x70\x33\x67\x70\x35',
      b'\x66\x74\x79\x70\x4d\x34\x56\x20',
      b'\x66\x74\x79\x70\x4d\x53\x4e\x56',
      b'\x66\x74\x79\x70\x66\x34\x76\x20',
      b'\x66\x74\x79\x70\x69\x73\x6f\x6d',
      b'\x66\x74\x79\x70\x6D\x70\x34\x32',
    }),
    _magic_item('application/applefile', 0, {
      b'\x00\x05\x16\x07'
    }),
  ]
  
  _NUM_BYTES = 32
  @classmethod
  def _guess_mime_type_with_magic_bytes(clazz, filename):
    with open(filename, 'rb') as fin:
      head = fin.read(clazz._NUM_BYTES)
      for item in clazz._MAGIC:
        offsetted_head = head[item.offset:]
        for signature in item.signatures:
          if offsetted_head.startswith(signature):
            return item.mime_type
    return None
