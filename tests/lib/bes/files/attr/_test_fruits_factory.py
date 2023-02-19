#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.attr.bfile_attr_handler_base import bfile_attr_handler_base

class _test_fruits_factory(bfile_attr_handler_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      ( 'acme/fruit/kiwi/1.0', clazz.decode_int, clazz.encode_int ),
      ( 'acme/fruit/cherry/2.0', clazz.decode_float, clazz.encode_float ),
      ( 'acme/fruit/price/1.0', clazz.decode_int, clazz.encode_int ),
    ]
