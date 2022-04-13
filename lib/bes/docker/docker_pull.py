#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.system.log import logger

from .docker_exe import docker_exe
from .docker_error import docker_error
from .docker_util import docker_util

class docker_pull(object):
  'Class to deal with docker pull.'
  
  _logger = logger('docker')

  @classmethod
  def pull(clazz, image_name, image_tag, non_blocking = False):
    check.check_string(image_name)
    check.check_string(image_tag, allow_none = True)

    docker_image = docker_util.make_tagged_image_name(image_name, image_tag)
    pull_args = [
      'pull',
      docker_image,
    ]
    rv = docker_exe.call_docker(pull_args, non_blocking = non_blocking)
    if rv.exit_code != 0:
      raise docker_error('failed to pull: {}'.format(' '.join(pull_args)))
