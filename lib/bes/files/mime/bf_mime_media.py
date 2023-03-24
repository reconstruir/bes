#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

class bf_mime_media(object):

  EXTENSIONS = frozenset([
    'asf',
    'avi',
    'divx',
    'flv',
    'gif',
    'jfif',
    'jpeg',
    'jpg',
    'm4v',
    'mkv',
    'mov',
    'mp4',
    'mp4v',
    'mpg4',
    'mpeg',
    'mpe',
    'm1v',
    'm2v',
    'mpg',
    'png',
    'ts',
    'webm',
    'webp',
    'wmv',
  ])

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
