#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .ci_unix_shell import ci_unix_shell

class ci_unix_shell_bash(ci_unix_shell):

  def __init__(self):
    super(ci_unix_shell_bash, self).__init__('bash', '/bin/bash', True)

  @classmethod
  #@abstractmethod
  def is_super_class(clazz):
    'Return True if this command interpreter class is a super class for other classes.'
    return False
