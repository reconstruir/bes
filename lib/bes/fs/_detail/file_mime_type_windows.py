#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import mimetypes
from bes.system.compat import compat
from bes.system.python import python

class file_mime_type_windows(object):
  'Determine mime type using the file utility on unix.'
    
  @classmethod
  def mime_type(clazz, filename):
    mime_type = clazz._guess_mime_type(filename)
    if not mime_type:
      mime_type, _ = mimetypes.guess_type(filename)
    return mime_type

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
  
