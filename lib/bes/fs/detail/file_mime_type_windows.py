#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import mimetypes

class file_mime_type_windows(object):
  'Determine mime type using the file utility on unix.'
    
  @classmethod
  def mime_type(clazz, filename):
    mime_type, charset = mimetypes.guess_type(filename)
    return ( mime_type, charset )
