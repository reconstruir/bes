#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class python_installer_error(Exception):
  def __init__(self, message, status_code = None):
    super(python_installer_error, self).__init__()
    self.message = message
    self.status_code = status_code

  def __str__(self):
    return self.message
