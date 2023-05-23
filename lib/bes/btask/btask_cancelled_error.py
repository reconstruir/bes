#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class btask_cancelled_error(Exception):
  def __init__(self, message):
    super().__init__(message)
    
    self.message = message

  def __str__(self):
    return self.message
