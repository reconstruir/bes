#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check

from bes.files.attr.bf_attr_desc_factory_base import bf_attr_desc_factory_base

from bes.files.attr.bf_attr_type_desc_bool import bf_attr_type_desc_bool
from bes.files.attr.bf_attr_type_desc_datetime import bf_attr_type_desc_datetime
from bes.files.attr.bf_attr_type_desc_float import bf_attr_type_desc_float
from bes.files.attr.bf_attr_type_desc_int import bf_attr_type_desc_int
from bes.files.attr.bf_attr_type_desc_string import bf_attr_type_desc_string

class fruits_factory(bf_attr_desc_factory_base):
      
  @classmethod
  #@abstractmethod
  def descriptions(clazz):
    return [
      (
        'acme__fruit__kiwi__1.0',
        'Kiwi',
        bf_attr_type_desc_int,
        None
      ),
      (
        'acme__fruit__cherry__2.0',
        'Cherry',
        bf_attr_type_desc_float,
        None
      ),
      (
        'acme__fruit__price__1.0',
        'Price',
        bf_attr_type_desc_int,
        None
      ),
      (
        'acme__fruit__birthday__1.0',
        'Birthday',
        bf_attr_type_desc_datetime,
        None
      ),
      (
        'acme__fruit__is_favorite__1.0',
        'Is Favorite',
        bf_attr_type_desc_bool,
        ( 'old_is_favorite1', 'old_is_favorite2' )
      ),
      (
        'acme__fruit__name__1.0',
        'Name',
        bf_attr_type_desc_string,
        None,
      ),
    ]
