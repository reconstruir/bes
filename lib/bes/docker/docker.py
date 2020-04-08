#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.system.host import host
from bes.fs.file_util import file_util

class docker(object):
  'Class to deal with docker.'

  _CGROUPS_FILE = '/proc/1/cgroup'
  
  @classmethod
  def is_running_inside_docker(clazz):
    if not host.is_linux():
      return False

    if not path.exists(clazz._CGROUPS_FILE):
      raise RuntimeError('cgroups file not found: {}'.format(clazz._CGROUPS_FILE))
    
    content = file_util.read(clazz._CGROUPS_FILE)
    return 'pids:/docker/' in content
