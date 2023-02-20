#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.files.attr.bfile_attr_value_factory_base import bfile_attr_value_factory_base

class fruits_factory(bfile_attr_value_factory_base):
      
  @classmethod
  #@abstractmethod
  def handlers(clazz):
    return [
      ( 'acme/fruit/kiwi/1.0', clazz.decode_int, clazz.encode_int, check.check_int ),
      ( 'acme/fruit/cherry/2.0', clazz.decode_float, clazz.encode_float, check.check_float ),
      ( 'acme/fruit/price/1.0', clazz.decode_int, clazz.encode_int, check.check_int ),
      ( 'acme/fruit/birthday/1.0', clazz.decode_datetime, clazz.encode_datetime, check.check_datetime ),
    ]
