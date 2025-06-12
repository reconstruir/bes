#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check

from bes.fs.dir_util import dir_util

from .bat_docker_images import bat_docker_images
from .bat_docker_exe import bat_docker_exe

class bat_docker_image_stash(object):

  @classmethod
  def save(clazz, blurber, repo, where, force):
    check.check_blurber(blurber)
    check.check_string(repo)
    check.check_string(where)
    check.check_bool(force)
                       
    images = bat_docker_images.list_images()
    images = images.matching_repository_pattern(repo)

    if not images:
      blurber.blurb('No images to stash found matching repo: "{}"'.format(repo))
      return 1

    if path.exists(where) and not path.isdir(where):
      blurber.blurb('Where should be a directory: "{}"'.format(where))
      return 1
      
    if path.exists(where) and not dir_util.is_empty(where):
      blurber.blurb('Where should be an empty directory: "{}"'.format(where))
      return 1

    for image in images:
      filename = '{}.tgz'.format(image.tagged_repository).replace('/', '_')
      output_archive = path.join(where, filename)
      blurber.blurb('Stashing {} in {}'.format(image.tagged_repository, output_archive))
      image.backup(output_archive)

    for image in images:
      bat_docker_images.remove(image.image_id, force = force)
      
    return 0

  @classmethod
  def restore(clazz, blurber, where):
    check.check_string(where)
                       
    if not path.exists(where):
      blurber.blurb('Stash directory not found: "{}"'.format(where))
      return 1
      
    if not path.isdir(where):
      blurber.blurb('Not a directory: "{}"'.format(where))
      return 1

    files = dir_util.list(where)
    if not files:
      blurber.blurb('No stash files found in: "{}"'.format(where))
      return 1

    for filename in files:
      args = [ 'load', '--input', filename ]
      bat_docker_exe.call_docker(args, non_blocking = False)
      
    return 0
