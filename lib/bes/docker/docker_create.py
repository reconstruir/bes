#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from bes.system.log import logger
from bes.fs.temp_file import temp_file
from bes.fs.file_util import file_util

from .docker_error import docker_error
from .docker_exe import docker_exe
from .docker_container import docker_container

class docker_create(object):
  'Class to deal with docker create.'
  
  _logger = logger('docker')

  @classmethod
  def create(clazz, image_id):
    'Create a container from an image.'
    args = [ 'create', image_id ]
    rv = docker_exe.call_docker(args, non_blocking = False)
    return rv.stdout.strip()

  @classmethod
  def copy_file(clazz, image_id, src_filename, dst_filename):
    if not path.isabs(src_filename):
      raise docker_error('src_filename should be an absolute path: {}'.format(src_filename))
    tmp = temp_file.make_temp_file()
    file_util.remove(tmp)
    container_id = None
    success = False
    try:
      container_id = clazz.create(image_id)
      args = [ 'cp', '{}:{}'.format(container_id, src_filename), tmp ]
      docker_exe.call_docker(args, non_blocking = False)
      if path.isfile(tmp):
        success = True
        file_util.rename(tmp, dst_filename)
    finally:
      if container_id:
        docker_container.remove_container(container_id)

    if not success:
      raise docker_error('failed to copy {} from {}'.format(src_filename, image_id))
