#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path
import re

from bes.common.algorithm import algorithm
from ..system.check import check
from bes.property.cached_property import cached_property
from bes.system.host import host
from bes.system.log import logger
from bes.files.bf_path import bf_path
from bes.fs.filename_util import filename_util

from .python_error import python_error
from .python_exe import python_exe
from .python_pip_exe import python_pip_exe
from .python_script import python_script
from .python_source import python_source
from .python_version import python_version

class python_exe_filename(object):
  'Class to deal with the python exe filename.'

  _log = logger('python')

  @classmethod
  def name(clazz, filename):
    check.check_string(filename)
    
    return python_source.exe_name(filename)
  
  @classmethod
  def version(clazz, exe_type, filename):
    check.check_string(exe_type)
    check.check_string(filename)
    
    name = python_source.exe_name(filename)
    f = re.findall(r'^{}(\d.*)$'.format(exe_type), name)
    if not f:
      return None
    return f[0]
