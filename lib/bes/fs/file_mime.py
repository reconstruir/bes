#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import fnmatch

from collections import OrderedDict

from bes.text.text_detect import text_detect
from bes.system.host import host

from .file_mime_type_detector import file_mime_type_detector

class file_mime(object):

  TEXT = 'text'

  BINARY_TYPES = set([
    'application/octet-stream',
    'application/x-dosexec',
    'application/x-executable',
    'application/x-mach-binary', # This is new in macos sierra
    'application/x-msdownload',
    'application/x-pie-executable',
    'application/x-sharedlib', # -pie vs -no-pie issue in gcc 7.3
  ])

  @classmethod
  def mime_type(clazz, filename):
    return file_mime_type_detector.detect_mime_type(filename)
    
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

  _MEDIA_TYPE_PATTERNS = OrderedDict( [
    ( 'video', 'video/*' ),
    ( 'image', 'image/*' ),
  ])

  MEDIA_TYPES = frozenset(_MEDIA_TYPE_PATTERNS.keys())
  
  @classmethod
  def media_type_for_file(clazz, filename):
    mime_type = clazz.mime_type(filename)
    return clazz.media_type_for_mime_type(mime_type)

  @classmethod
  def media_type_for_mime_type(clazz, mime_type):
    if mime_type == None:
      return None
    for media_type, pattern in clazz._MEDIA_TYPE_PATTERNS.items():
      if fnmatch.fnmatch(mime_type, pattern):
        return media_type
    return None
