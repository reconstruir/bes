#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.files.metadata.bf_metadata_factory_base import bf_metadata_factory_base
from bes.system.check import check

class example_metadata_fruits_factory(bf_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      (
        'acme/fruit/kiwi/1.0',
        'Kiwi',
        lambda f: os.stat(f).st_size,
        clazz.encoding.decode_int,
        clazz.encoding.encode_int,
        check.check_int,
        None
      ),
      (
        'acme/fruit/cherry/2.0',
        'Cherry',
        lambda f: float(os.stat(f).st_size / 2.0),
        clazz.encoding.decode_float,
        clazz.encoding.encode_float,
        check.check_float,
        None
      ),
      (
        'acme/fruit/melon/1.0',
        'Melon',
        lambda f: os.stat(f).st_size * 2,
        clazz.encoding.decode_int,
        clazz.encoding.encode_int,
        check.check_int,
        lambda f: clazz.metadata.get_cached_bytes_if_fresh(f, 'bes_double_size')
      )
    ]
