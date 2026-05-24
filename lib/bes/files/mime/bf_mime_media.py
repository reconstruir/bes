#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

class bf_mime_media(object):

  IMAGE_EXTENSIONS = frozenset([
    'gif',
    'jfif',
    'jpeg',
    'jpg',
    'png',
    'webp',
  ])

  VIDEO_EXTENSIONS = frozenset([
    'asf',
    'avi',
    'divx',
    'flv',
    'm1v',
    'm2v',
    'm4v',
    'mkv',
    'mov',
    'mp4',
    'mp4v',
    'mpe',
    'mpeg',
    'mpg',
    'mpg4',
    'ts',
    'webm',
    'wmv',
  ])

  EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

  MIME_TYPE_TO_EXT_MAP = {
    'image/gif': 'gif',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
    'video/divx': 'divx',
    'video/mp2t': 'ts',
    'video/mp4': 'mp4',
    'video/mpeg': 'mpeg',
    'video/quicktime': 'mov',
    'video/webm': 'webm',
    'video/x-flv': 'flv',
    'video/x-m4v': 'm4v',
    'video/x-matroska': 'mkv',
    'video/x-ms-asf': 'asf',
    'video/x-ms-wmv': 'wmv',
    'video/x-msvideo': 'avi',
  }
  def mime_type_to_extension(clazz, mime_type):
    check.check_string(mime_types)    

    return clazz.MIME_TYPE_TO_EXT_MAP.get(mime_type, None)
