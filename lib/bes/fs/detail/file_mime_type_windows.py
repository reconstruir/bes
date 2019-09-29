#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import mimetypes
from bes.system.compat import compat

class file_mime_type_windows(object):
  'Determine mime type using the file utility on unix.'
    
  @classmethod
  def mime_type(clazz, filename):
    mime_type, charset = clazz._guess_mime_type(filename)
    if not mime_type:
      mime_type, charset = mimetypes.guess_type(filename)
    charset = clazz._fudge_charset(filename, mime_type, charset)
    return ( mime_type, charset )

  @classmethod
  def _fudge_charset(clazz, filename, mime_type, charset):
    '''Fudge the charset to be compatible with the unix implementation.
    This is obviously bs and we need a better overall mime type strategy
    that is cross platform and doest fudge one thing a time.
    '''
    if mime_type == 'text/plain' and not charset:
      return 'us-ascii'
    return charset

  @classmethod
  def _guess_mime_type(clazz, filename):
    '''guess the mime type of a file.
    This is obviously bs and we need a better overall mime type strategy
    that is cross platform and doest fudge one thing a time.
    '''
    if clazz._is_python_code(filename):
      return 'text/x-python', 'us-ascii'
    elif clazz._is_zip(filename):
      return 'application/zip', 'binary'
    return None, None

  @classmethod
  def _is_python_code(clazz, filename):
    try:
      with open(filename, 'r') as fin:
        content = fin.read(32)
        return content.startswith('#!/usr/bin/env python3')
        return result
    except Exception as ex:
      pass
    return False

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
  
