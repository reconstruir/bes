#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.system.log import logger

from .bat_docker_exe import bat_docker_exe
from .bat_docker_error import bat_docker_error
from .bat_docker_util import bat_docker_util

class bat_docker_pull(object):
  'Class to deal with docker pull.'
  
  _logger = logger('docker')

  @classmethod
  def pull(clazz, image_name, image_tag, non_blocking = False):
    check.check_string(image_name)
    check.check_string(image_tag, allow_none = True)

    bat_docker_image = bat_docker_util.make_tagged_image_name(image_name, image_tag)
    pull_args = [
      'pull',
      bat_docker_image,
    ]
    rv = bat_docker_exe.call_docker(pull_args, non_blocking = non_blocking)
    if rv.exit_code != 0:
      raise bat_docker_error('failed to pull: {}'.format(' '.join(pull_args)))
