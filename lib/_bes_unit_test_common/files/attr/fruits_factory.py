#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.files.attr.bfile_attr_value_factory_base import bfile_attr_value_factory_base

class fruits_factory(bfile_attr_value_factory_base):
      
  @classmethod
  #@abstractmethod
  def descriptions(clazz):
    return [
      ( 'acme/fruit/kiwi/1.0', clazz.decode_int, clazz.encode_int, check.check_int, None ),
      ( 'acme/fruit/cherry/2.0', clazz.decode_float, clazz.encode_float, check.check_float, None ),
      ( 'acme/fruit/price/1.0', clazz.decode_int, clazz.encode_int, check.check_int, None ),
      ( 'acme/fruit/birthday/1.0', clazz.decode_datetime, clazz.encode_datetime, check.check_datetime, None ),
      ( 'acme/fruit/is_favorite/1.0', clazz.decode_bool, clazz.encode_bool, check.check_bool, ( 'old_is_favorite1', 'old_is_favorite2' ) ),
    ]
