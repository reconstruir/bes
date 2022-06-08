#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from .pyinstaller_log_level import pyinstaller_log_level

class pyinstaller_defaults:

  BUILD_DIR = path.join(os.getcwd(), 'BUILD')
  LOG_LEVEL = pyinstaller_log_level.INFO
  WINDOWED = False

  LOG_LEVEL_CHOICES = pyinstaller_log_level.values
  
