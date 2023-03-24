#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.system.log import logger

from ..metadata.bf_metadata import bf_metadata
from ..metadata.bf_metadata_factory_registry import bf_metadata_factory_registry

from .bf_metadata_factory_checksum import bf_metadata_factory_checksum
from .bf_metadata_factory_mime import bf_metadata_factory_mime

bf_metadata_factory_registry.register_factory(bf_metadata_factory_checksum)
bf_metadata_factory_registry.register_factory(bf_metadata_factory_mime)


  @classmethod
  def unregister_all_factories(clazz):
    bf_metadata_factory_registry.unregister_all()
