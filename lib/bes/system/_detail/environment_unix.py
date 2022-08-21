#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .environment_base import environment_base

class environment_unix(environment_base):

  @classmethod
  #@abstractmethod
  def home_dir_env(clazz, home_dir):
    'Return a dict with the environment needed to set the home directory.'

    return {
      'HOME': home_dir,
    }
