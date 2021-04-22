#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .python_source_base import python_source_base

class python_source_windows(python_source_base):

  @classmethod
  #@abstractmethod
  def exe_source(self, exe):
    'Return the source of the python executable.  Stuff like brew, xcode, system, python.org.'
    assert False

  @classmethod
  #@abstractmethod
  def possible_python_bin_dirs(self):
    'Return a list of possible dirs where the python executable might be.'
    return [
      r'C:\Program Files\Python37',
      r'C:\Program Files\Python38',
      r'C:\Program Files\Python39',
      r'C:\Python27',
    ]
