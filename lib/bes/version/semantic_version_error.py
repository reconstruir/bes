#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

class semantic_version_error(Exception):
  
  def __init__(self, message, position = None):
    check.check_string(message)
    check.check_point(position, allow_none = True)

    super(semantic_version_error, self).__init__()
    self.message = message
    self.position = position

  def __str__(self):
    if self.position:
      return 'error at position {}: {}'.format(self.position.x, self.message)
    else:
      return self.message
