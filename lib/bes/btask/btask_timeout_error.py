#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class btask_timeout_error(Exception):
  def __init__(self, message, timeout_seconds = None):
    super().__init__(message)
    self.message = message
    self.timeout_seconds = timeout_seconds

  def __str__(self):
    return self.message
