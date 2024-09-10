#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from ..system.check import check
from ..bcli.bcli_type_i import bcli_type_i

class dir_partition_criteria_base(object, metaclass = ABCMeta):

  @abstractmethod
  def classify(self, filename):
    'Return a string that classifies filename for dir partition.'
    raise NotImplemented('classify')
  
check.register_class(dir_partition_criteria_base, name = 'dir_partition_criteria', include_seq = False)

class cli_dir_partition_criteria(bcli_type_i):

  @classmethod
  #@abstractmethod
  def name_str(clazz):
    return 'dir_partition_criteria'

  @classmethod
  #@abstractmethod
  def type_function(clazz):
    return dir_partition_criteria_base

  @classmethod
  #@abstractmethod
  def parse(clazz, text):
    assert False
    return text

  @classmethod
  #@abstractmethod
  def check(clazz, value, allow_none = False):
    return check.check_dir_partition_criteria(value, allow_none = allow_none)
