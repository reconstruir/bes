#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib, json, os
from os import path

from bes.common.check import check
from bes.common.json_util import json_util
from bes.system.log import logger
from bes.text.text_line_parser import text_line_parser

from collections import namedtuple

from .docker_error import docker_error
from .docker_exe import docker_exe
from .docker_image import docker_image
from .docker_image_list import docker_image_list
from .docker_util import docker_util

class docker_images(object):
  'Class to deal with docker images.'
  
  _logger = logger('docker')

  @classmethod
  def list_images(clazz):
    format_parts = [
      '{{.ID}}',
      '{{.Repository}}',
      '{{.Tag}}',
      '{{.Digest}}',
      '{{.CreatedAt}}',
      '{{.Size}}',
    ]
    args = [
      'images',
      '--format', '@@@'.join(format_parts),
    ]
    rv = docker_exe.call_docker(args, non_blocking = False)
    lines = docker_util.parse_lines(rv.stdout)
    return docker_image_list([ clazz._parse_image(line) for line in lines ])

  @classmethod
  def list_untagged_images(clazz):
    all_images = clazz.list_images()
    return [ image for image in all_images if image.tag == None ]

  @classmethod
  def has_image(clazz, image):
    'Return True of we have image.  Can be an image id or tagged image name'
    check.check_string(image)

    try:
      clazz.inspect(image)
      return True
    except docker_error as ex:
      pass
    return False
  
  @classmethod
  def inspect(clazz, image):
    args = [ 'image', 'inspect', image ]
    rv = docker_exe.call_docker(args, non_blocking = False)
    return json_util.normalize_text(rv.stdout)
  
  @classmethod
  def inspect_checksum(clazz, image):
    text = clazz.inspect(image)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
  
  @classmethod
  def _parse_image(clazz, s):
    parts = s.split('@@@')
    assert len(parts) == 6
    size = parts.pop()
    created_at = parts.pop()
    digest = clazz._resolve_none(parts.pop())
    tag = clazz._resolve_none(parts.pop())
    repository = clazz._resolve_none(parts.pop())
    image_id = parts.pop()
    return docker_image(image_id, repository, tag, digest, created_at, size)

  @classmethod
  def _resolve_none(clazz, s):
    if s == '<none>':
      return None
    return s

  @classmethod
  def remove(clazz, image, force = False):
    check.check_string(image)

    args = [ 'rmi' ]
    if force:
      args.append('--force')
    args.append(image)
    docker_exe.call_docker(args, non_blocking = False)

  @classmethod
  def remove_all_untagged(clazz):
    images = clazz.list_untagged_images()
    for image in images:
      clazz.remove(image.image_id)

  @classmethod
  def pull(clazz, image):
    args = [ 'pull', image ]
    docker_exe.call_docker(args, non_blocking = False)
