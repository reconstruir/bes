#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.property.cached_class_property import cached_class_property
from bes.fs.file_util import file_util

class _test_ini_mixin:

  def demo_filename(clazz, filename):
    here = path.dirname(__file__)
    filename = path.join(here, filename)
    return path.abspath(filename)
  
  def demo_text(clazz, filename):
    return file_util.read(clazz.demo_filename(filename), codec = 'utf-8')
