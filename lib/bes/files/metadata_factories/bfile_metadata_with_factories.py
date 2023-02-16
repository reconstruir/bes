#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..metadata.bfile_metadata import bfile_metadata
from ..metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry

from .bfile_metadata_factory_checksum import bfile_metadata_factory_checksum
from .bfile_metadata_factory_mime import bfile_metadata_factory_mime

class bfile_metadata_with_factories(bfile_metadata):

  bfile_metadata_factory_registry.register_factory(bfile_metadata_factory_checksum)
  bfile_metadata_factory_registry.register_factory(bfile_metadata_factory_mime)

  @classmethod
  def unregister_all_factories(clazz):
    bfile_metadata_factory_registry.unregister_all()
