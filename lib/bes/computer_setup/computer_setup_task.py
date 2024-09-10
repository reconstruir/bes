#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from collections import namedtuple

from abc import abstractmethod, ABCMeta

from ..system.check import check
from bes.key_value.key_value_list import key_value_list
from bes.system.compat import compat

from .computer_setup_task_registry import computer_setup_task_registry

class _computer_setup_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'computer_setup_task':
      #print('register: {}'.format(clazz.__name__))
      computer_setup_task_registry.register(clazz)
    return clazz
  
class computer_setup_task(object, metaclass = _computer_setup_register_meta):

  @abstractmethod
  def name(self):
    'Name for task.'
    raise NotImplemented('name')

  @abstractmethod
  def description(self):
    'Description for task.'
    raise NotImplemented('description')

  @abstractmethod
  def average_duration(self):
    'Average duration in seconds.'
    raise NotImplemented('average_duration')

  @abstractmethod
  def is_needed(self):
    'Return True of the task needs to run.'
    raise NotImplemented('is_needed')

  @abstractmethod
  def run(self, options):
    'Run the task.'
    raise NotImplemented('run')

check.register_class(computer_setup_task, include_seq = False)
