#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import os.path as path

from .environment_base import environment_base

class environment_windows(environment_base):

  @classmethod
  #@abstractmethod
  def home_dir_env(clazz, home_dir):
    'Return a dict with the environment needed to set the home directory.'

    homedrive, homepath = path.splitdrive(home_dir)
    return {
      'HOME': home_dir,
      'HOMEDRIVE': homedrive,
      'HOMEPATH': homepath,
      'APPDATA': path.join(home_dir, 'AppData\\Roaming')
    }
