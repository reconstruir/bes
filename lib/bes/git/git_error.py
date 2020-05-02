#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class git_error(Exception):
  
  def __init__(self, message, execute_result = None):
    super(git_error, self).__init__()
    self.message = message
    self.execute_result = execute_result

  def __str__(self):
    return self.message
