#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from collections import namedtuple
#import copy
#import json
#import os
#from os import path
#import pprint

from bes.common.check import check
from bes.common.algorithm import algorithm
#from bes.fs.file_util import file_util
#from bes.fs.file_find import file_find
#from bes.fs.filename_util import filename_util
#from bes.property.cached_property import cached_property
#from bes.system.command_line import command_line
#from bes.system.env_var import env_var
#from bes.system.execute import execute
#from bes.system.host import host
from bes.system.log import logger
#from bes.system.os_env import os_env
#from bes.url.url_util import url_util
#
from .bes_project_error import bes_project_error
#from .pip_exe import pip_exe
from .bes_project_options import bes_project_options
#from .python_installation import python_installation
#from .python_source import python_source
#from .python_version import python_version
#from .python_virtual_env import python_virtual_env

from bes.python.python_exe import python_exe

class bes_project(object):
  'Bes project.'

  _log = logger('bes_project')
  
  def __init__(self, name, options = None):
    check.check_string(name)
    check.check_bes_project_options(options)

  def activate_script(self, variant = None):
    'Return the activate script for the virtual env'
    return 'foo'
  
  def setup(self, name, python_versions):
    'Setup'
    resolved_python_versions = self._resolve_python_versions(python_versions)

    available_versions = python_exe.available_versions()
    for python_version in resolved_python_versions:
      if not python_version in available_versions:
        versions_str = ' '.join(available_versions)
        raise bes_project_error('Python version "{}" not found.  Should be one of {}'.format(python_version,
                                                                                             versions_str))
    print('    name: {}'.format(name))
    print('versions: {}'.format(resolved_python_versions))

  @classmethod
  def _resolve_python_versions(clazz, python_versions):
    if not python_versions:
      return python_exe.default_exe_version()
    versions = clazz._flatten_python_versions(python_versions)
    result = []
    for next_version in versions:
      result.extend(clazz._resolve_one_version(next_version))
    return algorithm.unique(result)

  @classmethod
  def _resolve_one_version(clazz, python_version):
    if python_version == 'all':
      infos = python_exe.find_all_exes_info()
      return [ str(info.version) for _, info in infos.items() ]
    if python_version == 'latest':
      infos = python_exe.find_all_exes_info()
      if not infos:
        return []
      info = [ item[1] for item in infos.items() ][0]
      return [ str(info.version) ]
    return [ python_version ]

  @classmethod
  def _flatten_python_versions(clazz, python_versions):
    result = []
    for next_pv in python_versions:
      next_versions = [ pv.lower().strip() for pv in next_pv.split(',') ]
      result.extend(next_versions)
    return algorithm.unique(result)
  
