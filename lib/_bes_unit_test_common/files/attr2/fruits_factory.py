#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.files.attr.bf_attr2_desc_factory_base import bf_attr2_desc_factory_base

from bes.files.attr.bf_attr2_type_desc_bool import bf_attr2_type_desc_bool
from bes.files.attr.bf_attr2_type_desc_datetime import bf_attr2_type_desc_datetime
from bes.files.attr.bf_attr2_type_desc_float import bf_attr2_type_desc_float
from bes.files.attr.bf_attr2_type_desc_int import bf_attr2_type_desc_int
from bes.files.attr.bf_attr2_type_desc_string import bf_attr2_type_desc_string

class fruits_factory(bf_attr2_desc_factory_base):
      
  @classmethod
  #@abstractmethod
  def descriptions(clazz):
    return [
      (
        'acme/fruit/kiwi/1.0',
        'Kiwi',
        bf_attr2_type_desc_int,
        None
      ),
      (
        'acme/fruit/cherry/2.0',
        'Cherry',
        bf_attr2_type_desc_float,
        None
      ),
      (
        'acme/fruit/price/1.0',
        'Price',
        bf_attr2_type_desc_int,
        None
      ),
      (
        'acme/fruit/birthday/1.0',
        'Birthday',
        bf_attr2_type_desc_datetime,
        None
      ),
      (
        'acme/fruit/is_favorite/1.0',
        'Is Favorite',
        bf_attr2_type_desc_bool,
        ( 'old_is_favorite1', 'old_is_favorite2' )
      ),
      (
        'acme/fruit/name/1.0',
        'Name',
        bf_attr2_type_desc_string,
        None,
      ),
    ]
