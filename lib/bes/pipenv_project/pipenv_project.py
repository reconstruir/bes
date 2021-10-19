#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import os.path as path

from bes.common.check import check
from bes.pipenv.pipenv_exe import pipenv_exe
from bes.property.cached_property import cached_property
from bes.python.pip_project import pip_project
from bes.python.pip_project_options import pip_project_options
from bes.system.command_line import command_line
from bes.system.log import logger
from bes.text.tree_text_parser import tree_text_parser

from .pipenv_project_options import pipenv_project_options

class pipenv_project(object):
  'Pipenv project.'

  _log = logger('pipenv')
  
  def __init__(self, name, options = None):
    check.check_string(name)
    check.check_pipenv_project_options(options, allow_none = True)

    self._options = options or pipenv_project_options()
    pp_options = pip_project_options(debug = self._options.debug,
                                     verbose = self._options.verbose,
                                     blurber = self._options.blurber,
                                     root_dir = self._options.root_dir,
                                     python_version = self._options.python_version)
    self._pip_project = pip_project(name, pp_options)
    self._pipenv_cache_dir = path.join(self._pip_project.droppings_dir, 'pipenv-cache')
    extra_env = {
      'WORKON_HOME': self._pip_project.project_dir,
      'PIPENV_VENV_IN_PROJECT': '1',
      'PIPENV_CACHE_DIR': self._pipenv_cache_dir,
    }
    self._pip_project.extra_env = extra_env
    self._ensure_installed()

  @cached_property
  def pipfile_dir(self):
    if self._options.pipfile_dir:
      return self._options.pipfile_dir
    else:
      return self._pip_project.project_dir

  @cached_property
  def pipfile(self):
    return path.join(self.pipfile_dir, 'Pipfile')

  @cached_property
  def pipfile_lock(self):
    return path.join(self.pipfile_dir, 'Pipfile.lock')
  
  def pipenv_is_installed(self):
    return self._pip_project.has_program('pipenv')

  def check_pipenv_is_installed(self):
    if not self.pipenv_is_installed():
      raise pipenv_project_error('pipenv not installed')

  def pipfile_exists(self):
    return path.exists(self.pipfile)

  def pipfile_lock_exists(self):
    return path.exists(self.pipfile_lock)

  def check_pipfile_exists(self):
    if not self.pipfile_exists():
      raise pipenv_project_error('Pipfile does not exist: {}'.format(self.pipfile))

  def check_pipfile_lock_exists(self):
    if not self.pipfile_lock_exists():
      raise pipenv_project_error('Pipfile.lock does not exist: {}'.format(self.pipfile_lock))
    
  def pipenv_version(self):
    return pipenv_exe.version(self._pip_project.program_path('pipenv'))

  def call_pipenv(self, args, **kargs):
    command_line.check_args_type(args)

    kargs = copy.deepcopy(kargs)
    if 'cwd' in kargs:
      raise pipenv_project_error('Cannot override the cwd: "{}"'.format(kargs['cwd']))
    kargs['cwd'] = self.pipfile_dir
    args = [ 'pipenv' ] + list(args)
    return self._pip_project.call_program(args, **kargs)
  
  def _ensure_installed(self):
    self._ensure_pipenv_installed()
    self._ensure_pipfile_is_created()

  def _ensure_pipenv_installed(self):
    if self.pipenv_is_installed():
      return
    self._pip_project.install('pipenv', version = self._options.pipenv_version)

  def _ensure_pipfile_is_created(self):
    self.check_pipenv_is_installed()
    if self.pipfile_exists() and self.pipfile_lock_exists():
      return
    self.call_pipenv([ 'install' ])

  def install(self, packages, dev = False):
    check.check_string_seq(packages)
    check.check_bool(dev)

    dev_flags = [ '--dev' ] if dev else [] 
    args = [ 'install' ] + dev_flags + list(packages) 
    self.call_pipenv(args)

  def graph(self):
    rv = self.call_pipenv([ 'graph' ])
    tree = tree_text_parser.parse(rv.stdout, strip_comments = True)
    print(tree)
    return tree
