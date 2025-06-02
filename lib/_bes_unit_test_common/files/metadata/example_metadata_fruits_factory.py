#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.files.metadata.bf_metadata_factory_base import bf_metadata_factory_base
from bes.system.check import check

from bes.files.attr.bf_attr_type_desc_bool import bf_attr_type_desc_bool
from bes.files.attr.bf_attr_type_desc_datetime import bf_attr_type_desc_datetime
from bes.files.attr.bf_attr_type_desc_float import bf_attr_type_desc_float
from bes.files.attr.bf_attr_type_desc_int import bf_attr_type_desc_int
from bes.files.attr.bf_attr_type_desc_string import bf_attr_type_desc_string

class example_metadata_fruits_factory(bf_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def descriptions(clazz):
    return [
      (
        'acme__fruit__kiwi__1.0',
        'Kiwi',
        lambda f: os.stat(f).st_size,
        bf_attr_type_desc_int,
        None
      ),
      (
        'acme__fruit__cherry__2.0',
        'Cherry',
        lambda f: float(os.stat(f).st_size / 2.0),
        bf_attr_type_desc_float,
        None
      ),
      (
        'acme__fruit__melon__1.0',
        'Melon',
        lambda f: os.stat(f).st_size * 2,
        bf_attr_type_desc_int,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_double_size')
      )
    ]
