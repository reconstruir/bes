#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.files.metadata.bfile_metadata_factory_base import bfile_metadata_factory_base

class _test_fruits_factory(bfile_metadata_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      ( 'acme/fruit/kiwi/1.0', clazz._get_kiwi_1_0, clazz.decode_int, None ),
      ( 'acme/fruit/cherry/2.0', clazz._get_cherry_2_0, clazz.decode_float, None ),
      ( 'acme/fruit/price/1.0', None, clazz.decode_int, clazz.encode_int ),
    ]

  @classmethod
  def _get_kiwi_1_0(clazz, filename):
    return clazz.encode_int(os.stat(filename).st_size)

  @classmethod
  def _get_cherry_2_0(clazz, filename):
    return clazz.encode_float(os.stat(filename).st_size / 2.0)
