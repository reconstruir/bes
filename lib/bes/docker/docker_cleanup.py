#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing

from bes.common.check import check
from bes.system.log import logger

from .docker_images import docker_images
from .docker_container import docker_container

class docker_cleanup(object):
  'Class to deal with cleaning up docker side effects.'
  
  _logger = logger('docker')
  _lock = multiprocessing.Lock()
  
  @classmethod
  def cleanup(clazz, untagged_images = True, exited_containers = True, running_containers = False):
    clazz._lock.acquire()
    try:
      clazz._cleanup_i(untagged_images, exited_containers, running_containers)
      pass
    finally:
      clazz._lock.release()

  @classmethod
  def _cleanup_i(clazz, untagged_images, exited_containers, running_containers):
    if running_containers:
      docker_container.remove_all_running()
      
    if exited_containers:
      docker_container.remove_all_exited()

    if untagged_images:
      docker_images.remove_all_untagged()
