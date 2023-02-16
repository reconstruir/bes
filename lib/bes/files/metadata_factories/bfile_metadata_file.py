#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.property.cached_property import cached_property
from bes.system.check import check
from bes.system.log import logger

from .bfile_metadata_with_factories import bfile_metadata_with_factories

class bfile_metadata_file(object):

  _log = logger('bfile_metadata_with_factories_file')
  
  def __init__(self, filename):
    self._filename = filename

  @property
  def filename(self):
    return self._filename

  def get_metadata(self, domain, group, name, version):
    bfile_metadata_with_factories.check_part(domain)
    bfile_metadata_with_factories.check_part(group)
    bfile_metadata_with_factories.check_part(name)
    bfile_metadata_with_factories.check_part(version)
    
    return bfile_metadata_with_factories.get_metadata(self._filename,
                                                      domain,
                                                      group,
                                                      name,
                                                      version)
