#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import random

class brandom(object):

  @classmethod
  def initialize_seed(clazz, size = 1024):
    'Initialize the random seed using the crypto string os.urandom()'
    seed = os.urandom(1024)
    random.seed(seed)
