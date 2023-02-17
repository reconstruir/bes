#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..metadata.bfile_metadata_factory_registry import bfile_metadata_factory_registry

from .bfile_metadata_factory_checksum import bfile_metadata_factory_checksum
from .bfile_metadata_factory_mime import bfile_metadata_factory_mime

bfile_metadata_factory_registry.register_factory(bfile_metadata_factory_checksum)
bfile_metadata_factory_registry.register_factory(bfile_metadata_factory_mime)
