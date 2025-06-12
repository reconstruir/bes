#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from ..system.check import check
from bes.system.log import logger
from bes.text.text_line_parser import text_line_parser

from collections import namedtuple

from .bat_docker_exe import bat_docker_exe
from .bat_docker_util import bat_docker_util

class bat_docker_container(object):
  'Class to deal with docker containers.'
  
  _logger = logger('docker')

  _container = namedtuple('_container', 'container_id, image, status, size, names')
  @classmethod
  def list_containers(clazz):
    'Return a list of _container info tuples for all containers.'
    format_parts = [
      '{{.ID}}',
      '{{.Image}}',
      '{{.Status}}',
      '{{.Size}}',
      '{{.Names}}',
    ]
    args = [
      'ps',
      '--all',
      '--format', '@@@'.join(format_parts),
    ]
    rv = bat_docker_exe.call_docker(args, non_blocking = False)
    lines = bat_docker_util.parse_lines(rv.stdout)
    return [ clazz._parse_container(line) for line in lines ]

  @classmethod
  def last_container(clazz):
    'Return id of the last container that ran.'
    return bat_docker_exe.call_docker('ps --last 1 --quiet').stdout.strip()
        
  @classmethod
  def remove_container(clazz, container_id, force = False, volumes = False):
    'Remove the given container.'
    args = [ 'rm' ]
    if force:
      args.append('--force')
    if volumes:
      args.append('--volumes')
    args.append(container_id)
    bat_docker_exe.call_docker(args)
        
  @classmethod
  def _parse_container(clazz, s):
    parts = s.split('@@@')
    assert len(parts) == 5
    names = parts.pop()
    size = parts.pop()
    status = clazz._parse_status(parts.pop())
    image = parts.pop()
    container_id = parts.pop()
    return clazz._container(container_id, image, status, size, names)

  @classmethod
  def _parse_status(clazz, s):
    if s.startswith('Up'):
      return 'running'
    elif s.startswith('Exited'):
      return 'exited'
    elif s.startswith('Created'):
      return 'created'
    else:
      assert False

  @classmethod
  def remove_all_exited(clazz):
    'Remove all containers with the exited status.'
    containers = clazz.list_containers()
    for c in containers:
      if c.status == 'exited':
        clazz.remove_container(c.container_id)

  @classmethod
  def remove_all_running(clazz):
    'Remove all containers with the running status.'
    containers = clazz.list_containers()
    for c in containers:
      if c.status == 'running':
        clazz.remove_container(c.container_id, force = True)

  @classmethod
  def create(clazz, image_id):
    'Create a container with image_id.'
    return bat_docker_exe.call_docker('create {}'.format(image_id)).stdout.strip()

  @classmethod
  def copy_file_from(clazz, container_id, remote_filename, local_filename,
                     follow_link = False, archive_mode = False):
    'Copy a file from a container.'
    options =[]
    if follow_link:
      options.append('--follow-link')
    if archive_mode:
      options.append('--archive')
    cmd = [ 'cp' ] + options + [
      '{}:{}'.format(container_id, remote_filename),
      local_filename,
    ]
    bat_docker_exe.call_docker(cmd)
