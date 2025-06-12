#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.system.log import logger

from .bat_docker_error import bat_docker_error
from .bat_docker_exe import bat_docker_exe
from .bat_docker_util import bat_docker_util
from .bat_docker_images import bat_docker_images

class bat_docker_tag(object):
  'Class to deal with docker tag.'
  
  _logger = logger('docker')

  @classmethod
  def tag(clazz, source_repo, source_tag, target_repo, target_tag, non_blocking = False):
    check.check_string(source_repo)
    check.check_string(source_tag, allow_none = True)
    check.check_string(target_repo)
    check.check_string(target_tag, allow_none = True)

    if source_repo == target_repo:
      raise bat_docker_error('source_repo and target_repo are the same.')

    docker_source_repo = bat_docker_util.make_tagged_image_name(source_repo, source_tag)
    docker_target_repo = bat_docker_util.make_tagged_image_name(target_repo, target_tag)
    
    tag_args = [
      'tag',
      docker_source_repo,
      docker_target_repo,
    ]
    rv = bat_docker_exe.call_docker(tag_args, non_blocking = non_blocking)
    if rv.exit_code != 0:
      raise bat_docker_error('failed to tag: {}'.format(' '.join(tag_args)))

  @classmethod
  def tag_image(clazz, image_id, repo, tag):
    check.check_string(image_id)
    check.check_string(repo)
    check.check_string(tag)

    if not bat_docker_images.has_image(image_id):
      raise bat_docker_error('image not found: {}'.format(image_id))
    
    tagged_image_name = bat_docker_util.make_tagged_image_name(repo, tag)
    tag_args = [ 'tag', image_id, tagged_image_name ]
    rv = bat_docker_exe.call_docker(tag_args)
    if rv.exit_code != 0:
      raise bat_docker_error('failed to tag: {}'.format(' '.join(tag_args)))
    
