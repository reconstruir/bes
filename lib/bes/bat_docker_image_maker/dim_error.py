#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class dim_error(Exception):
  def __init__(self, message, exit_code = None):
    super(dim_error, self).__init__()
    self.message = message
    self.exit_code = exit_code

  def __str__(self):
    return self.message
