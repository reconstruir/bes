#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import multiprocessing

from ..system.check import check
from bes.system.log import logger

from .bat_docker_images import bat_docker_images
from .bat_docker_container import bat_docker_container

class bat_docker_cleanup(object):
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
      bat_docker_container.remove_all_running()
      
    if exited_containers:
      bat_docker_container.remove_all_exited()

    if untagged_images:
      bat_docker_images.remove_all_untagged()
