#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
#

from os import path
    
from bes.fs.file_util import file_util
from ..system.check import check
from bes.property.cached_property import cached_property

class dim_artifact_descriptor(object):

  def __init__(self, config, system_name, system_version, build_script, build_dir):
    self.config = config
    self.system_name = system_name
    self.system_version = system_version
    self.build_script = build_script
    self.build_dir = build_dir

  def __str__(self):
    return '{}-{}-{}'.format(self.name, self.system_name, self.system_version)
      
  # TODO: need to change self.build_script to be a comprehensive list of inputs
  # such as the openssl tarball for python
  @cached_property
  def filename(self):
    build_script_checksum = file_util.checksum('sha256', self.build_script)[0:32]
    basename = '{}-{}-{}-{}.tar.gz'.format(self.name, self.version, self.system_name, self.system_version)
    return path.join(self.build_dir, 'artifacts', self.name, build_script_checksum, basename)
      
  @property
  def name(self):
    return self.config.header_.name
  
  @property
  def version(self):
    return self.config.version

  @property
  def depends(self):
    return self.config.get_string_list('depends')
