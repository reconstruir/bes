#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.property.cached_class_property import cached_class_property

from ._detail._bf_attr2_getter_super_class import _bf_attr2_getter_super_class
from .bf_attr2_getter_base import bf_attr2_getter_base

class bf_attr2(bf_attr2_getter_base):

  def __init__(self):
    super().__init__(self._impl_instance)

  @cached_class_property
  def _impl_instance(clazz):
    return _bf_attr2_getter_super_class()
