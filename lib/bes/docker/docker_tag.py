#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.system.log import logger

from .docker_error import docker_error
from .docker_exe import docker_exe
from .docker_util import docker_util
from .docker_images import docker_images

class docker_tag(object):
  'Class to deal with docker tag.'
  
  _logger = logger('docker')

  @classmethod
  def tag(clazz, source_repo, source_tag, target_repo, target_tag, non_blocking = False):
    check.check_string(source_repo)
    check.check_string(source_tag, allow_none = True)
    check.check_string(target_repo)
    check.check_string(target_tag, allow_none = True)

    if source_repo == target_repo:
      raise docker_error('source_repo and target_repo are the same.')

    docker_source_repo = docker_util.make_tagged_image_name(source_repo, source_tag)
    docker_target_repo = docker_util.make_tagged_image_name(target_repo, target_tag)
    
    tag_args = [
      'tag',
      docker_source_repo,
      docker_target_repo,
    ]
    rv = docker_exe.call_docker(tag_args, non_blocking = non_blocking)
    if rv.exit_code != 0:
      raise docker_error('failed to tag: {}'.format(' '.join(tag_args)))

  @classmethod
  def tag_image(clazz, image_id, repo, tag):
    check.check_string(image_id)
    check.check_string(repo)
    check.check_string(tag)

    if not docker_images.has_image(image_id):
      raise docker_error('image not found: {}'.format(image_id))
    
    tagged_image_name = docker_util.make_tagged_image_name(repo, tag)
    tag_args = [ 'tag', image_id, tagged_image_name ]
    rv = docker_exe.call_docker(tag_args)
    if rv.exit_code != 0:
      raise docker_error('failed to tag: {}'.format(' '.join(tag_args)))
    
