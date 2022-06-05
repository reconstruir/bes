#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

class pyinstaller_defaults:

  BUILD_DIR = path.join(os.getcwd(), 'BUILD')
  LOG_LEVEL = 'INFO'
  WINDOWED = False
