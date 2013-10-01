#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os.path as path, os

class FileUtil(object):
  @classmethod
  def mkdir(clazz, p):
    if path.isdir(p):
      return
    os.makedirs(p)
                  
