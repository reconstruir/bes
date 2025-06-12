#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from bes.text.text_table import text_table

from bes.cli.cli_command_handler import cli_command_handler
from bes.fs.dir_util import dir_util
from bes.fs.file_util import file_util
from bes.script.blurber import blurber as script_blurber
from bes.system.log import logger

from .bat_docker_cleanup import bat_docker_cleanup
from .bat_docker_cli_options import bat_docker_cli_options
from .bat_docker_container import bat_docker_container
from .bat_docker_image_stash import bat_docker_image_stash
from .bat_docker_images import bat_docker_images

class bat_docker_cli_handler(cli_command_handler):

  _log = logger('docker')
  
  def __init__(self, cli_args):
    super().__init__(cli_args, options_class = bat_docker_cli_options)
  
  def images(self, untagged, repo, style):
    check.check_bool(untagged)
    check.check_string(repo, allow_none = True)
    check.check_string(style)

    images = bat_docker_images.list_images()
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

  def backup(self, tagged_repository, output_archive):
    check.check_string(tagged_repository)

    images = bat_docker_images.list_images()
    image = images.find_image(tagged_repository)
    if not image:
      self.options.blurber.blurb('Image not found: "{}"'.format(tagged_repository))
      return 1

    image.backup(output_archive)
    
    return 0
  
  def stash_save(self, repo, where, force):
    check.check_string(repo)
    check.check_string(where)
    check.check_bool(force)

    return bat_docker_image_stash.save(self.options.blurber, repo, where, force)

  def stash_restore(self, where):
    check.check_string(where)
                       
    return bat_docker_image_stash.restore(self.options.blurber, where)
  
  def ps(self, brief, status):
    containers = bat_docker_container.list_containers()
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
  
  def image_inspect(self, image, checksum):

    if checksum:
      chk = bat_docker_images.inspect_checksum(image)
      print(chk)
    else:
      data = bat_docker_images.inspect(image)
      print(data)
    return 0

  def cleanup(self, untagged_images, exited_containers, running_containers):
    bat_docker_cleanup.cleanup(untagged_images, exited_containers, running_containers)
    return 0
