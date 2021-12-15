#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from collections import OrderedDict

from bes.text.text_detect import text_detect
from bes.system.host import host

class file_mime(object):

  TEXT = 'text'

  BINARY_TYPES = [
    'application/x-sharedlib', # -pie vs -no-pie issue in gcc 7.3
    'application/octet-stream',
    'application/x-executable',
    'application/x-pie-executable',
    'application/x-mach-binary', # This is new in macos sierra
    'application/x-msdownload',
  ]

  @classmethod
  def mime_type(clazz, filename):
    impl = clazz._get_impl()
    assert impl
    t = impl.mime_type(filename)
    return t
    
  @classmethod
  def is_text(clazz, filename):
    return clazz.mime_type_is_text(filename) or text_detect.file_is_text(filename)

  @classmethod
  def mime_type_is_text(clazz, filename):
    return clazz.mime_type(filename).startswith(clazz.TEXT)

  @classmethod
  def is_binary(clazz, filename):
    return clazz.mime_type(filename) in clazz.BINARY_TYPES

  _GZIP_MIME_TYPES = [ 'application/x-gzip', 'application/gzip', 'application/x-tar' ]
  _ZIP_MIME_TYPES = [ 'application/zip', 'application/x-zip-compressed' ]
  
  @classmethod
  def is_gzip(clazz, filename):
    return clazz.mime_type(filename) in clazz._GZIP_MIME_TYPES

  @classmethod
  def is_zip(clazz, filename):
    return clazz.mime_type(filename) in clazz._ZIP_MIME_TYPES

  @classmethod
  def _get_impl(clazz):
    if not hasattr(clazz, '_mime_type_impl'):
      impl = None
      if host.is_unix():
        from ._detail.file_mime_type_unix_file_exe import file_mime_type_unix_file_exe
        impl = file_mime_type_unix_file_exe
      elif host.is_windows():
        from ._detail.file_mime_type_windows import file_mime_type_windows
        impl = file_mime_type_windows
      else:
        raise RuntimeError('Unknown system: {}'.format(host.SYSTEM))
      assert impl
      setattr(clazz, '_mime_type_impl', impl)
    return getattr(clazz, '_mime_type_impl', None)
  
  _MEDIA_TYPE_PATTERNS = OrderedDict( [
    ( 'video', 'video/*' ),
    ( 'image', 'image/*' ),
  ])

  MEDIA_TYPES = frozenset(_MEDIA_TYPE_PATTERNS.keys())
  
  @classmethod
  def media_type(clazz, filename):
    mt = clazz.mime_type(filename)
    if mt == None:
      return 'unknown'
    for media_type, pattern in clazz._MEDIA_TYPE_PATTERNS.items():
      if fnmatch.fnmatch(mt, pattern):
        return media_type
    return 'unknown'
