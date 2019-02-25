#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import os, sys
from os import path
#from collections import namedtuple
from bes.system import os_env_var

class shell_profile(object):
  'Class to hack shell profile files such as ~/.bash_profile and ~/.bashrc.'

  @classmethod
  def shell_is_bash(clazz):
    'Return True if the current shell is bash.'
    v = os_env_var('SHELL')
    if v.is_set:
      return 'bash' in v.value
    v = os_env_var('BASH')
    if v.is_set:
      return 'bash' in v.value
    return False
