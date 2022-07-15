#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .hconfig_origin import hconfig_origin

class hconfig_error(Exception):
  
  def __init__(self, message, origin = None):
    check.check_string(message)
    check.check_hconfig_origin(origin, allow_none = True)
    
    super().__init__()
    self.message = message
    self.origin = origin

  def __str__(self):
    blurbs = []
    if self.origin and self.origin.source:
      blurbs.append(self.origin.source)
    else:
      blurbs.append('<unknown>')
    if self.origin and self.origin.line_number is not None:
      blurbs.append(str(self.origin.line_number))
      
    return '{}: {}'.format(':'.join(blurbs), self.message)
