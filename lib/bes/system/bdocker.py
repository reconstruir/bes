#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from functools import wraps

from bes.system.host import host
from bes.fs.file_util import file_util
from bes.testing.unit_test_class_skip import unit_test_class_skip

class bdocker(object):
  'Class to deal with docker.'

  _CGROUPS_FILE = '/proc/1/cgroup'
  _FORCE_IS_RUNNING_UNDER_DOCKER = None
  
  @classmethod
  def is_running_inside_docker(clazz):
    if clazz._FORCE_IS_RUNNING_UNDER_DOCKER != None:
      return clazz._FORCE_IS_RUNNING_UNDER_DOCKER
    
    if not host.is_linux():
      return False

    if not path.exists(clazz._CGROUPS_FILE):
      raise RuntimeError('cgroups file not found: {}'.format(clazz._CGROUPS_FILE))
    
    content = file_util.read(clazz._CGROUPS_FILE, codec = 'utf-8')
    return 'pids:/docker/' in content

  @staticmethod
  def raise_skip_if_running_under_docker():
    unit_test_class_skip.raise_skip_if(not bdocker.is_running_inside_docker(), 'running under docker')

class is_running_under_docker_override(object):
  'A class with context support for overriding whether running under docker.  Mostly for unit testing.'
  
  def __init__(self, running_under_docker):
    assert isinstance(running_under_docker, bool)
    self._running_under_docker = running_under_docker
    
  def __enter__(self):
    bdocker._FORCE_IS_RUNNING_UNDER_DOCKER = self._running_under_docker
    return self
  
  def __exit__(self, type, value, traceback):
    bdocker._FORCE_IS_RUNNING_UNDER_DOCKER = None

def is_running_under_docker_override_func(running_under_docker):
  'A decarator that calls is_running_under_docker_override.'
  def _wrap(func):
    @wraps(func)
    def _caller(self, *args, **kwargs):
      with is_running_under_docker_override(running_under_docker) as over:
        return func(self, *args, **kwargs)
    return _caller
  return _wrap
