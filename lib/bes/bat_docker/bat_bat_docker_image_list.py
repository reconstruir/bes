#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from bes.common.type_checked_list import type_checked_list

from .bat_docker_image import bat_docker_image

class bat_bat_docker_image_list(type_checked_list):
  'A list of docker images'

  __value_type__ = bat_docker_image
  
  def __init__(self, values = None):
    super(bat_bat_docker_image_list, self).__init__(values = values)

  def untagged(self):
    'Return a new list with only untagged images'
    return bat_bat_docker_image_list([ image for image in self if image.tag == None ])

  def matching_repository_pattern(self, pattern):
    'Return a new list with images for which repository matches pattern'
    return bat_bat_docker_image_list([ image for image in self if image.repository_matches(pattern) ])

  def find_image(self, tagged_repository):
    'Find an image that matches tagged_repository or None if not found.'
    for image in self:
      if image.tagged_repository == tagged_repository:
        return image
    return None
  
check.register_class(bat_bat_docker_image_list, include_seq = False)
