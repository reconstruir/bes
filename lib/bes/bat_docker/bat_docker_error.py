#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bat_docker_error(Exception):
  def __init__(self, message, exit_code = None):
    super(bat_docker_error, self).__init__()
    self.message = message
    self.exit_code = exit_code

  def __str__(self):
    return self.message
