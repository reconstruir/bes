#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.files.metadata.bfile_metadata_factory_base import bfile_metadata_factory_base

class _test_fruits_factory(bfile_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      ( 'acme/fruit/kiwi/1.0', lambda f: os.stat(f).st_size, clazz.decode_int, clazz.encode_int, True ),
      ( 'acme/fruit/cherry/2.0', lambda f: float(os.stat(f).st_size / 2.0), clazz.decode_float, clazz.encode_float, True ),
      ( 'acme/fruit/price/1.0', None, clazz.decode_int, clazz.encode_int, False ),
    ]
