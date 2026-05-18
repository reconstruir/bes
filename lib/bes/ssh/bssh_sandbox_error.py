#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bssh_sandbox_error(Exception):
  def __init__(self, message='dunno'):
    super(bssh_sandbox_error, self).__init__()
    self.message = message

  def __str__(self):
    return self.message
