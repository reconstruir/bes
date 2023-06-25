#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.files.attr.bf_attr_handler_factory_base import bf_attr_handler_factory_base

class fruits_factory(bf_attr_handler_factory_base):
      
  @classmethod
  #@abstractmethod
  def descriptions(clazz):
    return [
      (
        'acme/fruit/kiwi/1.0',
        'Kiwi',
        clazz.encoding.decode_int,
        clazz.encoding.encode_int,
        check.check_int,
        None
      ),
      (
        'acme/fruit/cherry/2.0',
        'Cherry',
        clazz.encoding.decode_float,
        clazz.encoding.encode_float,
        check.check_float,
        None
      ),
      (
        'acme/fruit/price/1.0',
        'Price',
        clazz.encoding.decode_int,
        clazz.encoding.encode_int,
        check.check_int,
        None
      ),
      (
        'acme/fruit/birthday/1.0',
        'Birthday',
        clazz.encoding.decode_datetime,
        clazz.encoding.encode_datetime,
        check.check_datetime,
        None
      ),
      (
        'acme/fruit/is_favorite/1.0',
        'Is Favorite',
        clazz.encoding.decode_bool,
        clazz.encoding.encode_bool,
        check.check_bool,
        ( 'old_is_favorite1', 'old_is_favorite2' )
      ),
      (
        'acme/fruit/name/1.0',
        'Name',
        clazz.encoding.decode_string,
        clazz.encoding.encode_string,
        check.check_string,
        None,
      ),
    ]
