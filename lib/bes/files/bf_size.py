#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .bf_check import bf_check

class bf_size(object):
  
  # from https://gist.github.com/cbwar/d2dfbc19b140bd599daccbe0fe925597
  @classmethod
  def format_size(clazz, num, suffix = None):
    """Readable file size
    :param num: Bytes value
    :type num: int
    :param suffix: Optional suffix or None
    :type suffix: str
    :rtype: str
    """
    suffix = suffix or ''
    for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
      if abs(num) < 1024.0:
        return "%3.1f%s%s" % (num, unit, suffix)
      num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)    
    
  # https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
  @classmethod
  def sizeof_fmt(clazz, num, suffix = 'B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
      if abs(num) < 1024.0:
        return "%3.1f%s%s" % (num, unit, suffix)
      num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
