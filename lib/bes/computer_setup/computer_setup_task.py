#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from abc import abstractmethod, ABCMeta

from bes.common.check import check
from bes.system.compat import with_metaclass
from bes.system.compat import compat

from .computer_setup_registry import computer_setup_registry

class _computer_setup_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    if name != 'computer_setup_base':
      computer_setup_registry.register(clazz)
    return clazz
  
class computer_setup_task(with_metaclass(_computer_setup_register_meta, object)):

  def __init__(self, options = None):
    options = options or computer_setup_options()
    check.check_computer_setup_options(options)
    self.options = options

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
    raise NotImplemented('run')

  @abstractmethod
  def run(self):
    'Run the task.'
    raise NotImplemented('run')

  @property
  def blurber(self):
    return self.options.blurber
  
  def blurb(self, message, output = None, fit = False):
    self.blurber.blurb(message, output = output, fit = fit)
    
  def blurb_verbose(self, message, output = None, fit = False):
    self.blurber.blurb_verbose(message, output = output, fit = fit)

check.register_class(computer_setup_task, include_seq = False)
