#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.python.pip_project_options import pip_project_options

from .pipenv_project_error import pipenv_project_error

class pipenv_project_options(pip_project_options):

  def __init__(self, **kargs):
    super(pipenv_project_options, self).__init__(**kargs)

  @classmethod
  #@abstractmethod
  def default_values(clazz):
    'Return a dict of defaults for these options.'
    return clazz.super_default_values({
      'isolated_cache_dir': False,
      'pipenv_version': None,
      'pipfile_dir': None,
    })
  
  @classmethod
  #@abstractmethod
  def value_type_hints(clazz):
    return clazz.super_value_type_hints({
      'isolated_cache_dir': bool,
    })

  @classmethod
  #@abstractmethod
  def error_class(clazz):
    return pipenv_project_error

  #@abstractmethod
  def check_value_types(self):
    'Check the type of each option.'
    super(pipenv_project_options, self).check_value_types()
    check.check_bool(self.isolated_cache_dir)
    check.check_string(self.pipfile_dir, allow_none = True)
    check.check_string(self.pipenv_version, allow_none = True)
    
check.register_class(pipenv_project_options)
