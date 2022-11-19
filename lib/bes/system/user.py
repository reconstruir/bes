#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from .environment import environment

class user(object):

  @classmethod
  def home(self):
    return environment.home_dir()

  @classmethod
  def username(self):
    return environment.username()
