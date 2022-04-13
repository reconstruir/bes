#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from bes.text.text_table import text_table

from bes.fs.dir_util import dir_util
from bes.fs.file_util import file_util
from bes.script.blurber import blurber as script_blurber

from .docker_cleanup import docker_cleanup
from .docker_container import docker_container
from .docker_images import docker_images
from .docker_image_stash import docker_image_stash

class docker_cli_command(object):

  @classmethod
  def handle_command(clazz, command, **kargs):
    func = getattr(clazz, command)
    return func(script_blurber(), **kargs)
  
  @classmethod
  def images(clazz, blurber, untagged, repo, style):
    check.check_blurber(blurber)
    check.check_bool(untagged)
    check.check_string(repo, allow_none = True)
    check.check_string(style)

    images = docker_images.list_images()
    if untagged:
      images = images.untagged()

    if repo:
      images = images.matching_repository_pattern(repo)

    if not images:
      return 0
      
    if style == 'brief':
      for image in images:
        print(image.image_id)
    elif style == 'table':
      tt = text_table(data = images)
      tt.set_labels( ( 'ID', 'REPOSITORY', 'TAG', 'DIGEST', 'CREATED_AT', 'SIZE' ) )
      print(tt)
    elif style == 'repo':
      for image in images:
        print(image.tagged_repository)
    return 0

  @classmethod
  def backup(clazz, blurber, tagged_repository, output_archive):
    check.check_string(tagged_repository)

    images = docker_images.list_images()
    image = images.find_image(tagged_repository)
    if not image:
      blurber.blurb('Image not found: "{}"'.format(tagged_repository))
      return 1

    image.backup(output_archive)
    
    return 0
  
  @classmethod
  def stash_save(clazz, blurber, repo, where, force):
    check.check_blurber(blurber)
    check.check_string(repo)
    check.check_string(where)
    check.check_bool(force)

    return docker_image_stash.save(blurber, repo, where, force)

  @classmethod
  def stash_restore(clazz, blurber, where):
    check.check_blurber(blurber)
    check.check_string(where)
                       
    return docker_image_stash.restore(blurber, where)
  
  @classmethod
  def ps(clazz, blurber, brief, status):
    check.check_blurber(blurber)

    containers = docker_container.list_containers()
    if status:
      containers = [ c for c in containers if c.status == status ]
    if not containers:
      return 0
    if brief:
      for container in containers:
        print(container.container_id)
      return 0
    tt = text_table(data = containers)
    tt.set_labels( ( 'ID', 'IMAGE', 'STATUS', 'SIZE', 'NAMES' ) )
    print(tt)
    return 0
  
  @classmethod
  def image_inspect(clazz, blurber, image, checksum):
    check.check_blurber(blurber)

    if checksum:
      chk = docker_images.inspect_checksum(image)
      print(chk)
    else:
      data = docker_images.inspect(image)
      print(data)
    return 0

  @classmethod
  def cleanup(clazz, blurber, untagged_images, exited_containers, running_containers):
    check.check_blurber(blurber)

    docker_cleanup.cleanup(untagged_images, exited_containers, running_containers)
    return 0
