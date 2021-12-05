#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class ads_error(Exception):
  
  def __init__(self, message, exit_code = None):
    super(ads_error, self).__init__()
    self.message = message

  def __str__(self):
    return self.message
