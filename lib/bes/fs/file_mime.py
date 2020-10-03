#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from __future__ import division

from collections import namedtuple
from bes.compat.map import map
from bes.system.compat import compat
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

  # FIXME: some illegal seuqences cause this to choke: /Users/ramiro/software/tmp/builds/flex-2.6.0_rev1_2016-02-07-05-14-52-769130/deps/installation/share/gettext/po/boldquot.sed 

  class _mime_type_and_charset(namedtuple('_mime_type_and_charset', 'mime_type, charset')):

    def __new__(clazz, mime_type, charset):
      return clazz.__bases__[0].__new__(clazz, mime_type, charset)
  
    def __str__(self):
      return '%s; charset=%s' % (self.mime_type, self.charset)

    def __hash__(self):
      return hash(str(self))
    
  @classmethod
  def mime_type(clazz, filename):
    impl = clazz._get_impl()
    assert impl
    t = impl.mime_type(filename)
    return clazz._mime_type_and_charset(t[0], t[1])
    
  @classmethod
  def is_text(clazz, filename):
    return clazz.mime_type_is_text(filename) or clazz.content_is_text(filename)

  @classmethod
  def mime_type_is_text(clazz, filename):
    return clazz.mime_type(filename).mime_type.startswith(clazz.TEXT)

  @classmethod
  def is_binary(clazz, filename):
    return clazz.mime_type(filename).mime_type in clazz.BINARY_TYPES

  _GZIP_MIME_TYPES = [ 'application/x-gzip', 'application/gzip', 'application/x-tar' ]
  _ZIP_MIME_TYPES = [ 'application/zip', 'application/x-zip-compressed' ]
  
  @classmethod
  def is_gzip(clazz, filename):
    return clazz.mime_type(filename).mime_type in clazz._GZIP_MIME_TYPES

  @classmethod
  def is_zip(clazz, filename):
    return clazz.mime_type(filename).mime_type in clazz._ZIP_MIME_TYPES

  @classmethod
  def content_is_text(clazz, filename):
    if compat.IS_PYTHON2:
      return clazz._content_is_text_py2(filename)
    else:
      return clazz._content_is_text_py3(filename)

  # From https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
  @classmethod
  def _content_is_text_py3(clazz, filename):
    try:
      with open(filename, "r") as f:
        for l in f:
          pass
      return True
    except UnicodeDecodeError:
      return False

  @classmethod
  def _content_is_text_py2(clazz, filename):
    with open(filename, 'rb') as fin:
      s = fin.read(512)
      text_characters = ''.join(list(map(chr, range(32, 127))) + list('\n\r\t\b'))
      if compat.IS_PYTHON2:
        import string
        _null_trans = string.maketrans('', '')
      else:
        _null_trans = bytes.maketrans(b'', b'')
        
      if not s:
        # Empty files are considered text
        return True
      if b'\0' in s:
        # Files with null bytes are likely binary
        return False
      # Get the non-text characters (maps a character to itself then
      # use the 'remove' option to get rid of the text characters.)
      t = s.translate(_null_trans, text_characters)
      # If more than 30% non-text characters, then
      # this is considered a binary file
      if float(len(t))/float(len(s)) > 0.30:
        return False
      return True  
    
  @classmethod
  def _get_impl(clazz):
    if not hasattr(clazz, '_mime_type_impl'):
      impl = None
      if host.is_unix():
        from .detail.file_mime_type_unix_file_exe import file_mime_type_unix_file_exe
        impl = file_mime_type_unix_file_exe
      elif host.is_windows():
        from .detail.file_mime_type_windows import file_mime_type_windows
        impl = file_mime_type_windows
      else:
        raise RuntimeError('Unknown system: {}'.format(host.SYSTEM))
      assert impl
      setattr(clazz, '_mime_type_impl', impl)
    return getattr(clazz, '_mime_type_impl', None)
