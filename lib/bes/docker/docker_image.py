#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import fnmatch

from bes.property.cached_property import cached_property
from bes.common.check import check
from bes.fs.temp_file import temp_file
from bes.fs.file_util import file_util
from bes.fs.compressed_file import compressed_file
from bes.system.execute import execute

from .docker_util import docker_util
from .docker_exe import docker_exe

class docker_image(namedtuple('docker_image', 'image_id, repository, tag, digest, created_at, size')):

  def __new__(clazz, image_id, repository, tag, digest, created_at, size):
    check.check_string(image_id)
    check.check_string(repository)
    check.check_string(tag)
    check.check_string(digest, allow_none = True)
    check.check_string(created_at)
    check.check_string(size)

    return clazz.__bases__[0].__new__(clazz, image_id, repository, tag, digest, created_at, size)

  @cached_property
  def tagged_repository(self):
    'Return a string in the repo:tag format.'
    return docker_util.make_tagged_image_name(self.repository, self.tag)

  def repository_matches(self, pattern):
    'Return True of the repository matches pattern using fnmatch.'
    return fnmatch.fnmatch(self.repository, pattern)

  def backup(self, output_archive):
    'Backup image to an gzipped tarball.'
    tmp_tar = temp_file.make_temp_file(suffix = '.tar')
    args = [ 'save', self.tagged_repository, '-o', tmp_tar ]
    docker_exe.call_docker(args, non_blocking = False)
    compressed_file.compress(tmp_tar, output_archive)
    file_util.remove(tmp_tar)
  
check.register_class(docker_image, include_seq = False)
