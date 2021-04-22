#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
import subprocess

from .python_source_base import python_source_base
from bes.system.compat import compat

class python_source_macos(python_source_base):

  @classmethod
  #@abstractmethod
  def exe_source(self, exe):
    'Return the source of the python executable.  Stuff like brew, xcode, system, python.org.'
    raise NotImplemented('exe_source')

  @classmethod
  #@abstractmethod
  def possible_python_bin_dirs(self):
    'Return a list of possible dirs where the python executable might be.'
    return [
      '/opt/local/bin',
      '/usr/bin',
      '/usr/local/bin',
      '/usr/local/opt/python@3.7/bin',
      '/usr/local/opt/python@3.8/bin',
      '/usr/local/opt/python@3.9/bin',
    ]
