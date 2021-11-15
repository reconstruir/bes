#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.debug.debug_timer import debug_timer
from bes.debug.debug_timer import timed_method
from bes.fs.file_check import file_check
from bes.python.pip_project import pip_project
from bes.python.pip_project_options import pip_project_options
from bes.python.python_exe import python_exe
from bes.system.log import logger

from .bes_project_error import bes_project_error
from .bes_project_options import bes_project_options

class bes_project(object):
  'Bes project.'

  _log = logger('bes_project')
  _timer = debug_timer('bes_project', disabled = True) #, level = 'error')
  
  def __init__(self, options = None):
    check.check_bes_project_options(options, allow_none = True)

    self._options = options or bes_project_options()

  def activate_script(self, variant = None):
    'Return the activate script for the virtual env'
    return 'foo'
  
  @timed_method('_timer')
  def ensure(self, versions, requirements, requirements_dev = None):
    'Ensure a bes project is ensured'
    check.check_string_seq(versions)
    requirements = file_check.check_file(requirements)
    requirements_dev = file_check.check_file(requirements_dev, allow_none = True)

    print('CACA: requirements={}'.format(requirements))
    print('CACA: requirements_dev={}'.format(requirements_dev))
    
    self._timer.start('resolve')
    resolved_versions = self._resolve_versions(versions)
    self._timer.stop()
    self._timer.start('available')
    available_versions = python_exe.available_versions()
    self._timer.stop()
    self._timer.start('check')
    for python_version in resolved_versions:
      if not python_version in available_versions:
        versions_str = ' '.join(available_versions)
        raise bes_project_error('Python version "{}" not found.  Should be one of {}'.format(python_version,
                                                                                             versions_str))

    self._timer.stop()
    self._timer.start('infos')
    infos = python_exe.find_all_exes_info(key_by_version = True)
    self._timer.stop()

    self._timer.start('ensure_all')
    for python_version in resolved_versions:
      assert python_version in infos
      info = infos[python_version]
      pp_root_dir = path.join(self._options.root_dir, python_version)
      if not path.isdir(pp_root_dir):
        self._timer.start('ensure_{}'.format(python_version))
        pp_options = pip_project_options(debug = self._options.debug,
                                         verbose = self._options.verbose,
                                         blurber = self._options.blurber,
                                         root_dir = pp_root_dir,
                                         python_exe = info.exe)
        pp = pip_project(pp_options)
        self._timer.stop()
    self._timer.stop()

  @timed_method('_timer')
  def _resolve_versions(self, versions):
    result = []
    if not versions:
      self._timer.start('_resolve_versions: call default_exe_version()')
      result = [ str(python_exe.default_exe_version()) ]
      self._timer.stop()
    else:
      self._timer.start('_resolve_versions: call _flatten_versions()')
      flat_versions = self._flatten_versions(versions)
      self._timer.stop()
      for next_version in flat_versions:
        self._timer.start('_resolve_versions: call _resolve_one_version()')
        result.extend(self._resolve_one_version(next_version))
        self._timer.stop()
    return algorithm.unique(result)

  @timed_method('_timer')
  def _resolve_one_version(self, python_version):
    infos = python_exe.find_all_exes_info()
    if python_version in [ 'all', 'all3' ]:
      return [ str(info.version) for _, info in infos.items() if info.version.major_version == 3 ]
    elif python_version == 'all2':
      return [ str(info.version) for _, info in infos.items() if info.version.major_version == 2 ]
    elif python_version == 'all23':
      return [ str(info.version) for _, info in infos.items() ]
    elif python_version == 'latest':
      if not infos:
        return []
      info = [ item[1] for item in infos.items() ][0]
      return [ str(info.version) ]
    return [ python_version ]

  @timed_method('_timer')
  def _flatten_versions(self, versions):
    result = []
    for next_version in versions:
      next_versions = [ pv.lower().strip() for pv in str(next_version).split(',') ]
      result.extend(next_versions)
    return algorithm.unique(result)
